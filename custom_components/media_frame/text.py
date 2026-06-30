"""Text platform — color and time-string settings via REST PATCH."""

from __future__ import annotations

from homeassistant.components.text import TextEntity, TextMode
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
        MediaFrameSettingText(coordinator, definition)
        for definition in SETTING_DEFS_BY_KIND["text"]
    )


class MediaFrameSettingText(MediaFrameSettingEntity, TextEntity):
    """Text entity for hex colors and HH:MM night-mode times."""

    def __init__(self, coordinator: MediaFrameCoordinator, definition) -> None:
        super().__init__(coordinator, definition)
        self._attr_mode = TextMode.TEXT
        if definition.key in {
            "slideshowNightModeFrom",
            "slideshowNightModeTo",
        }:
            self._attr_mode = TextMode.TEXT
            self._attr_native_max = 5
        else:
            self._attr_native_max = 32

    @property
    def native_value(self) -> str | None:
        raw = self._raw_setting_value()
        if raw is None:
            return None
        return str(raw)

    async def async_set_value(self, value: str) -> None:
        await self.coordinator.api.patch_settings({self._setting_key: value.strip()})
        await self.coordinator.async_request_refresh()
