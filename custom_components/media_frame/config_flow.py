"""Config flow for Media Frame."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.typing import ConfigType

from .api import MediaFrameApi, MediaFrameApiError, MediaFrameAuthError, MediaFrameConnectionError
from .const import CONF_TOKEN, DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
            vol.Coerce(int), vol.Range(min=1024, max=65535)
        ),
        vol.Required(CONF_TOKEN): str,
    }
)


async def _validate_api(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    session = aiohttp_client.async_get_clientsession(hass)
    api = MediaFrameApi(
        session,
        data[CONF_HOST],
        data[CONF_TOKEN],
        data.get(CONF_PORT, DEFAULT_PORT),
    )
    health = await api.validate()
    identity = await api.get_group_identity()
    if not health.get("ok"):
        raise MediaFrameConnectionError("health check failed")
    return {"health": health, "identity": identity}


class MediaFrameConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Media Frame."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Options flow handler."""
        return MediaFrameOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await _validate_api(self.hass, user_input)
            except MediaFrameAuthError:
                errors["base"] = "invalid_auth"
            except MediaFrameConnectionError:
                errors["base"] = "cannot_connect"
            except MediaFrameApiError:
                errors["base"] = "unknown"
            else:
                host = user_input[CONF_HOST]
                await self.async_set_unique_id(f"{host}:{user_input[CONF_PORT]}")
                self._abort_if_unique_id_configured()
                title = _device_title(info)
                return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )

    async def async_step_import(self, import_config: ConfigType) -> config_entries.FlowResult:
        """Import from configuration.yaml (optional legacy)."""
        return await self.async_step_user(import_config)


class MediaFrameOptionsFlowHandler(config_entries.OptionsFlow):
    """Options — scan interval could be added later."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        return self.async_create_entry(title="", data=self.config_entry.options)


def _device_title(info: dict[str, Any]) -> str:
    identity = info.get("identity") or {}
    health = info.get("health") or {}
    name = str(identity.get("deviceName") or "").strip()
    model = str(health.get("deviceModel") or "").strip()
    host = str(health.get("lanIpv4") or "").strip()
    if name:
        return name
    if model and host:
        return f"Media Frame {model} ({host})"
    if model:
        return f"Media Frame {model}"
    return "Media Frame"
