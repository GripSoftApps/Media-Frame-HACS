"""Button platform — REST integration actions."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MediaFrameCoordinator

BUTTONS: tuple[tuple[str, str, dict | None, str], ...] = (
    ("roon_connect", "roon/connect", {}, "mdi:lan-connect"),
    ("roon_pause", "roon/transport", {"control": "pause"}, "mdi:pause"),
    ("roon_play", "roon/transport", {"control": "play"}, "mdi:play"),
    ("musicid_listen_now", "musicid/listenNow", {}, "mdi:microphone"),
    ("google_cast_discover", "googledevices/discover", {}, "mdi:cast-connected"),
    ("restart_app", "system/restartApp", {}, "mdi:restart"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MediaFrameCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        MediaFrameActionButton(coordinator, key, op, body, icon) for key, op, body, icon in BUTTONS
    )


class MediaFrameActionButton(CoordinatorEntity[MediaFrameCoordinator], ButtonEntity):
    """Fire-and-forget (with optional wait) integration POST."""

    def __init__(
        self,
        coordinator: MediaFrameCoordinator,
        translation_key: str,
        op: str,
        body: dict | None,
        icon: str,
    ) -> None:
        super().__init__(coordinator)
        self._op = op
        self._body = body
        self._attr_translation_key = translation_key
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_btn_{translation_key}"
        self._attr_icon = icon
        self._attr_device_info = coordinator.device_info

    async def async_press(self) -> None:
        await self.coordinator.api.post_action_and_wait(self._op, self._body)
        await self.coordinator.async_request_refresh()
