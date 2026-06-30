"""Number platform — numeric settings via REST PATCH."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MediaFrameCoordinator

NUMBER_SETTINGS: tuple[tuple[str, str, float, float, float, str], ...] = (
    ("slideshow_idle_sec", "slideshowIdleSec", 3, 600, 1, "s"),
    ("slideshow_image_sec", "slideshowImageSec", 3, 120, 1, "s"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MediaFrameCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        MediaFrameSettingNumber(coordinator, t_key, s_key, min_v, max_v, step, unit)
        for t_key, s_key, min_v, max_v, step, unit in NUMBER_SETTINGS
    )


class MediaFrameSettingNumber(CoordinatorEntity[MediaFrameCoordinator], NumberEntity):
    """Number entity mapped to an integer setting."""

    def __init__(
        self,
        coordinator: MediaFrameCoordinator,
        translation_key: str,
        setting_key: str,
        min_value: float,
        max_value: float,
        step: float,
        unit: str,
    ) -> None:
        super().__init__(coordinator)
        self._setting_key = setting_key
        self._attr_translation_key = translation_key
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_num_{setting_key}"
        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        self._attr_native_step = step
        self._attr_native_unit_of_measurement = unit
        self._attr_mode = NumberMode.BOX
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> float | None:
        raw = self.coordinator.data.settings.get(self._setting_key)
        if raw is None:
            return None
        try:
            return float(raw)
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.api.patch_settings({self._setting_key: round(value)})
        await self.coordinator.async_request_refresh()
