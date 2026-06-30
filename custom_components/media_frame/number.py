"""Number platform — numeric settings via REST PATCH."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
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
        MediaFrameSettingNumber(coordinator, definition)
        for definition in SETTING_DEFS_BY_KIND["number"]
    )


class MediaFrameSettingNumber(MediaFrameSettingEntity, NumberEntity):
    """Number entity mapped to an integer/float setting."""

    def __init__(self, coordinator: MediaFrameCoordinator, definition) -> None:
        super().__init__(coordinator, definition)
        self._attr_native_min_value = definition.min_value
        self._attr_native_max_value = definition.max_value
        self._attr_native_step = definition.step
        if definition.unit:
            self._attr_native_unit_of_measurement = definition.unit
        self._attr_mode = NumberMode.BOX

    @property
    def native_value(self) -> float | None:
        raw = self._raw_setting_value()
        if raw is None:
            return None
        try:
            return float(raw)
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        payload = round(value) if self._definition.step == 1 else value
        await self.coordinator.api.patch_settings({self._setting_key: payload})
        await self.coordinator.async_request_refresh()
