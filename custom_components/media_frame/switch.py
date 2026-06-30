"""Switch platform — boolean settings via REST PATCH."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
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
        MediaFrameSettingSwitch(coordinator, definition)
        for definition in SETTING_DEFS_BY_KIND["switch"]
    )


class MediaFrameSettingSwitch(MediaFrameSettingEntity, SwitchEntity):
    """Switch mapped to a boolean settings key."""

    @property
    def is_on(self) -> bool:
        return self._raw_setting_value() is True

    async def async_turn_on(self, **kwargs) -> None:
        await self._patch(True)

    async def async_turn_off(self, **kwargs) -> None:
        await self._patch(False)

    async def _patch(self, value: bool) -> None:
        await self.coordinator.api.patch_settings({self._setting_key: value})
        await self.coordinator.async_request_refresh()
