"""DataUpdateCoordinator for Media Frame REST polling."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MediaFrameApi, MediaFrameApiError, MediaFrameAuthError, MediaFrameConnectionError
from .const import CONF_HOST, CONF_PORT, CONF_TOKEN, DEFAULT_SCAN_INTERVAL, DOMAIN, INTEGRATION_STATUS_KEYS

_LOGGER = logging.getLogger(__name__)


class MediaFrameData:
    """Cached REST payloads."""

    def __init__(self) -> None:
        self.health: dict[str, Any] = {}
        self.identity: dict[str, Any] = {}
        self.settings: dict[str, Any] = {}
        self.integrations: dict[str, dict[str, Any]] = {}
        self.roon_zones: dict[str, Any] = {}
        self.group: dict[str, Any] = {}


class MediaFrameCoordinator(DataUpdateCoordinator[MediaFrameData]):
    """Poll health, settings, and integration status snapshots."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, api: MediaFrameApi) -> None:
        self.api = api
        self.data = MediaFrameData()
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
            config_entry=entry,
        )

    async def _async_update_data(self) -> MediaFrameData:
        data = MediaFrameData()
        try:
            data.health = await self.api.get_health()
            data.identity = await self.api.get_group_identity()
            data.settings = await self.api.get_settings()
            data.roon_zones = await self.api.get_roon_zones()
            data.group = await self.api.get_group_status()
            for key in INTEGRATION_STATUS_KEYS:
                try:
                    data.integrations[key] = await self.api.get_integration_status(key)
                except MediaFrameApiError as err:
                    _LOGGER.debug("integration status %s: %s", key, err)
                    data.integrations[key] = {"ok": False, "error": str(err)}
        except MediaFrameAuthError as err:
            raise UpdateFailed("invalid REST token") from err
        except MediaFrameConnectionError as err:
            raise UpdateFailed(f"cannot reach tablet REST API: {err}") from err
        except MediaFrameApiError as err:
            raise UpdateFailed(str(err)) from err
        self.data = data
        return data

    @property
    def device_info(self) -> DeviceInfo:
        """Device registry entry for this tablet."""
        health = self.data.health
        identity = self.data.identity
        name = str(identity.get("deviceName") or "").strip() or "Media Frame"
        return DeviceInfo(
            identifiers={(DOMAIN, self.config_entry.entry_id)},
            name=name,
            manufacturer="Media Frame",
            model=str(health.get("deviceModel") or "Android tablet"),
            sw_version=str(health.get("version") or ""),
            configuration_url=str(health.get("webUiUrl") or "") or None,
        )


async def async_create_api(hass: HomeAssistant, entry: ConfigEntry) -> MediaFrameApi:
    """Build API client from config entry."""
    session = async_get_clientsession(hass)
    return MediaFrameApi(
        session,
        entry.data[CONF_HOST],
        entry.data[CONF_TOKEN],
        entry.data.get(CONF_PORT, 8787),
    )
