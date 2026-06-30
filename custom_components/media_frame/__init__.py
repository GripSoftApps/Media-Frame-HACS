"""The Media Frame integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv, entity_registry as er

from .const import DOMAIN
from .coordinator import MediaFrameCoordinator, async_create_api

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.BUTTON,
    Platform.NUMBER,
]

SERVICE_PATCH_SETTINGS = "patch_settings"
SERVICE_CALL_ACTION = "call_action"

PATCH_SCHEMA = vol.Schema(
    {
        vol.Required("patch"): dict,
    }
)

CALL_ACTION_SCHEMA = vol.Schema(
    {
        vol.Required("action"): cv.string,
        vol.Optional("body"): dict,
        vol.Optional("wait", default=True): cv.boolean,
    }
)


def _config_entry_from_service(hass: HomeAssistant, call: ServiceCall) -> ConfigEntry:
    entity_ids = list(call.target.get("entity_id", [])) if call.target else []
    if not entity_ids:
        raise HomeAssistantError("service requires a Media Frame entity target")
    registry = er.async_get(hass)
    if not (entity_entry := registry.async_get(entity_ids[0])):
        raise HomeAssistantError(f"unknown entity {entity_ids[0]}")
    entry_id = entity_entry.config_entry_id
    if not entry_id or entry_id not in hass.data.get(DOMAIN, {}):
        raise HomeAssistantError("entity is not a Media Frame device")
    entry = hass.config_entries.async_get_entry(entry_id)
    if entry is None:
        raise HomeAssistantError("Media Frame config entry not found")
    return entry


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Media Frame from a config entry."""
    api = await async_create_api(hass, entry)
    coordinator = MediaFrameCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    if not hass.services.has_service(DOMAIN, SERVICE_PATCH_SETTINGS):

        async def handle_patch(call: ServiceCall) -> None:
            cfg_entry = _config_entry_from_service(hass, call)
            api_client = hass.data[DOMAIN][cfg_entry.entry_id]["api"]
            coord: MediaFrameCoordinator = hass.data[DOMAIN][cfg_entry.entry_id]["coordinator"]
            await api_client.patch_settings(call.data["patch"])
            await coord.async_request_refresh()

        async def handle_action(call: ServiceCall) -> dict[str, Any]:
            cfg_entry = _config_entry_from_service(hass, call)
            api_client = hass.data[DOMAIN][cfg_entry.entry_id]["api"]
            coord: MediaFrameCoordinator = hass.data[DOMAIN][cfg_entry.entry_id]["coordinator"]
            action = str(call.data["action"]).strip().lstrip("/")
            body = call.data.get("body") or {}
            if call.data.get("wait", True):
                result = await api_client.post_action_and_wait(action, body)
            else:
                result = await api_client.post_action(action, body)
            await coord.async_request_refresh()
            return result

        hass.services.async_register(
            DOMAIN,
            SERVICE_PATCH_SETTINGS,
            handle_patch,
            schema=PATCH_SCHEMA,
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_CALL_ACTION,
            handle_action,
            schema=CALL_ACTION_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_PATCH_SETTINGS)
            hass.services.async_remove(DOMAIN, SERVICE_CALL_ACTION)
    return unload_ok
