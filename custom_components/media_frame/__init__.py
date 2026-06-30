"""The Media Frame integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID, Platform
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

PATCH_SCHEMA = cv.make_entity_service_schema(
    {
        vol.Required("patch"): dict,
    }
)

CALL_ACTION_SCHEMA = cv.make_entity_service_schema(
    {
        vol.Required("action"): cv.string,
        vol.Optional("body", default={}): dict,
        vol.Optional("wait", default=True): cv.boolean,
    }
)


def _entry_for_entity(hass: HomeAssistant, entity_id: str) -> ConfigEntry:
    registry = er.async_get(hass)
    if not (entry := registry.async_get(entity_id)):
        raise HomeAssistantError(f"unknown entity {entity_id}")
    entry_id = entry.config_entry_id
    if not entry_id or entry_id not in hass.data.get(DOMAIN, {}):
        raise HomeAssistantError("entity is not a Media Frame device")
    return hass.config_entries.async_get_entry(entry_id)


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
            entity_id = call.data[ATTR_ENTITY_ID]
            cfg_entry = _entry_for_entity(hass, entity_id)
            api_client = hass.data[DOMAIN][cfg_entry.entry_id]["api"]
            coord: MediaFrameCoordinator = hass.data[DOMAIN][cfg_entry.entry_id]["coordinator"]
            await api_client.patch_settings(call.data["patch"])
            await coord.async_request_refresh()

        async def handle_action(call: ServiceCall) -> dict[str, Any]:
            entity_id = call.data[ATTR_ENTITY_ID]
            cfg_entry = _entry_for_entity(hass, entity_id)
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
