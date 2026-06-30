"""Shared entity base for Media Frame setting entities."""

from __future__ import annotations

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import MediaFrameCoordinator
from .ha_settings import SettingDef


class MediaFrameSettingEntity(CoordinatorEntity[MediaFrameCoordinator], Entity):
    """Base for entities backed by a REST settings key."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: MediaFrameCoordinator, definition: SettingDef) -> None:
        super().__init__(coordinator)
        self._definition = definition
        self._setting_key = definition.key
        self._attr_translation_key = definition.translation_key
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_setting_{definition.key}"
        self._attr_icon = definition.icon
        self._attr_device_info = coordinator.device_info
        # Explicit fallback so entities never collapse to the device name only.
        self._attr_name = definition.name_en

    def _raw_setting_value(self):
        return self.coordinator.data.settings.get(self._setting_key)
