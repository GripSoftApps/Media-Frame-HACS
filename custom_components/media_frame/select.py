"""Select platform — enum settings via REST PATCH."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import MediaFrameCoordinator
from .entity import MediaFrameSettingEntity
from .ha_settings import SETTING_DEFS_BY_KIND


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MediaFrameCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        MediaFrameSettingSelect(coordinator, definition)
        for definition in SETTING_DEFS_BY_KIND["select"]
    )


class MediaFrameSettingSelect(MediaFrameSettingEntity, SelectEntity):
    """Select entity for string enum settings."""

    def __init__(self, coordinator: MediaFrameCoordinator, definition) -> None:
        super().__init__(coordinator, definition)
        self._attr_options = list(definition.options)

    @property
    def current_option(self) -> str | None:
        raw = self._raw_setting_value()
        if raw is None:
            return None
        value = str(raw)
        return value if value in self._attr_options else None

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.api.patch_settings({self._setting_key: option})
        await self.coordinator.async_request_refresh()
