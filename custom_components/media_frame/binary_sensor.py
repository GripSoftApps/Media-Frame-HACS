"""Binary sensor platform for Media Frame integrations."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MediaFrameCoordinator

BINARY_DESCRIPTIONS: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key="rest_online",
        translation_key="rest_online",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    BinarySensorEntityDescription(
        key="slideshow_enabled",
        translation_key="slideshow_enabled",
        icon="mdi:image-multiple",
    ),
    BinarySensorEntityDescription(
        key="roon_connected",
        translation_key="roon_connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    BinarySensorEntityDescription(
        key="appletv_connected",
        translation_key="appletv_connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    BinarySensorEntityDescription(
        key="musicid_listening",
        translation_key="musicid_listening",
        icon="mdi:ear-hearing",
    ),
    BinarySensorEntityDescription(
        key="google_cast_available",
        translation_key="google_cast_available",
        icon="mdi:cast",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MediaFrameCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities: list[MediaFrameBinarySensor] = [
        MediaFrameBinarySensor(coordinator, desc) for desc in BINARY_DESCRIPTIONS
    ]
    async_add_entities(entities)


class MediaFrameBinarySensor(CoordinatorEntity[MediaFrameCoordinator], BinarySensorEntity):
    """Binary sensors derived from REST snapshots."""

    entity_description: BinarySensorEntityDescription

    def __init__(
        self,
        coordinator: MediaFrameCoordinator,
        description: BinarySensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool | None:
        key = self.entity_description.key
        health = self.coordinator.data.health
        settings = self.coordinator.data.settings
        integrations = self.coordinator.data.integrations

        if key == "rest_online":
            return health.get("ok") is True
        if key == "slideshow_enabled":
            return settings.get("slideshowEnabled") is True
        if key == "roon_connected":
            roon = integrations.get("roon") or {}
            return roon.get("ok") is True or roon.get("transportAttached") is True
        if key == "appletv_connected":
            atv = integrations.get("appletv") or {}
            return atv.get("ok") is True
        if key == "musicid_listening":
            ms = integrations.get("musicid") or {}
            return ms.get("listening") is True
        if key == "google_cast_available":
            gd = integrations.get("googledevices") or {}
            devices = gd.get("devices")
            if isinstance(devices, list) and len(devices) > 0:
                return True
            return gd.get("ok") is True and int(gd.get("deviceCount") or 0) > 0
        return None

    @property
    def extra_state_attributes(self) -> dict:
        key = self.entity_description.key
        integrations = self.coordinator.data.integrations
        if key == "roon_connected":
            return {k: v for k, v in (integrations.get("roon") or {}).items()}
        if key == "appletv_connected":
            return dict(integrations.get("appletv") or {})
        if key == "musicid_listening":
            return dict(integrations.get("musicid") or {})
        if key == "google_cast_available":
            return dict(integrations.get("googledevices") or {})
        return {}
