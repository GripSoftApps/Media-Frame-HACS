"""Switch platform — toggles settings via REST PATCH."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MediaFrameCoordinator

SETTING_SWITCHES: tuple[tuple[str, str, str], ...] = (
    ("slideshow_enabled", "slideshowEnabled", "mdi:image-multiple"),
    ("roon_enabled", "roonEnabled", "mdi:music-circle"),
    ("apple_tv_enabled", "appleTvEnabled", "mdi:apple"),
    ("musicid_enabled", "musicIdEnabled", "mdi:ear-hearing"),
    ("google_devices_enabled", "googleDevicesEnabled", "mdi:cast"),
    ("remember_last_played", "rememberLastPlayedOnWake", "mdi:history"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MediaFrameCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        MediaFrameSettingSwitch(coordinator, translation_key, setting_key, icon)
        for translation_key, setting_key, icon in SETTING_SWITCHES
    )


class MediaFrameSettingSwitch(CoordinatorEntity[MediaFrameCoordinator], SwitchEntity):
    """Switch mapped to a boolean settings key."""

    def __init__(
        self,
        coordinator: MediaFrameCoordinator,
        translation_key: str,
        setting_key: str,
        icon: str,
    ) -> None:
        super().__init__(coordinator)
        self._setting_key = setting_key
        self._attr_translation_key = translation_key
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_switch_{setting_key}"
        self._attr_icon = icon
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.settings.get(self._setting_key) is True

    async def async_turn_on(self, **kwargs) -> None:
        await self._patch(True)

    async def async_turn_off(self, **kwargs) -> None:
        await self._patch(False)

    async def _patch(self, value: bool) -> None:
        await self.coordinator.api.patch_settings({self._setting_key: value})
        await self.coordinator.async_request_refresh()
