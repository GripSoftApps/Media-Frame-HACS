"""Sensor platform for Media Frame."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MediaFrameCoordinator

SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="app_version",
        translation_key="app_version",
        icon="mdi:tablet",
    ),
    SensorEntityDescription(
        key="battery",
        translation_key="battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class="battery",
        icon="mdi:battery",
    ),
    SensorEntityDescription(
        key="cpu",
        translation_key="cpu",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:chip",
    ),
    SensorEntityDescription(
        key="roon_zones_count",
        translation_key="roon_zones_count",
        icon="mdi:speaker-multiple",
    ),
    SensorEntityDescription(
        key="musicid_mic_dbfs",
        translation_key="musicid_mic_dbfs",
        icon="mdi:microphone",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MediaFrameCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(MediaFrameSensorEntity(coordinator, desc) for desc in SENSOR_DESCRIPTIONS)


class MediaFrameSensorEntity(CoordinatorEntity[MediaFrameCoordinator], SensorEntity):
    """Representation of a Media Frame sensor."""

    entity_description: SensorEntityDescription

    def __init__(
        self,
        coordinator: MediaFrameCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> str | int | float | None:
        key = self.entity_description.key
        health = self.coordinator.data.health
        settings = self.coordinator.data.settings
        integrations = self.coordinator.data.integrations

        if key == "app_version":
            return str(health.get("versionDisplay") or health.get("version") or "")
        if key == "battery":
            pct = health.get("batteryPct")
            return float(pct) if pct is not None else None
        if key == "cpu":
            pct = health.get("cpuPct")
            return float(pct) if pct is not None else None
        if key == "roon_zones_count":
            zones = self.coordinator.data.roon_zones.get("zones")
            if isinstance(zones, list):
                return len(zones)
            roon = integrations.get("roon") or {}
            return int(roon.get("zonesCount") or 0)
        if key == "musicid_mic_dbfs":
            ms = integrations.get("musicid") or {}
            level = ms.get("micLevelDbfs")
            return float(level) if level is not None else None
        return None

    @property
    def extra_state_attributes(self) -> dict:
        key = self.entity_description.key
        health = self.coordinator.data.health
        if key == "app_version":
            return {
                "version_code": health.get("versionCode"),
                "lan_ipv4": health.get("lanIpv4"),
                "web_ui_url": health.get("webUiUrl"),
                "device_model": health.get("deviceModel"),
            }
        if key == "battery":
            return {"charging": health.get("batteryCharging")}
        if key == "musicid_mic_dbfs":
            ms = self.coordinator.data.integrations.get("musicid") or {}
            return {
                "listening": ms.get("listening"),
                "effective_gate_dbfs": ms.get("effectiveGateDbfs"),
                "last_match_title": ms.get("lastMatchTitle"),
                "last_match_artist": ms.get("lastMatchArtist"),
            }
        return {}
