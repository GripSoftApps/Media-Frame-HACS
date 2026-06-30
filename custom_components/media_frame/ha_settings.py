"""Home Assistant entity catalog — basic appearance, slideshow, integration toggles.

Excludes connection flows (pairing, hosts, tokens) and transport actions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

SettingKind = Literal["switch", "select", "number", "text"]

_CAMEL_TO_SNAKE = re.compile(r"(?<!^)(?=[A-Z])")


def api_value_to_ha_state_key(value: str) -> str:
    """Map REST enum token to homeassistant translation key [a-z0-9_]."""
    snake = _CAMEL_TO_SNAKE.sub("_", value).lower()
    return re.sub(r"[^a-z0-9_]+", "_", snake).strip("_")


def build_select_option_maps(
    options: tuple[str, ...],
) -> tuple[tuple[str, ...], dict[str, str], dict[str, str]]:
    """Return HA option keys, ha->api map, api->ha map (unique per option list)."""
    ha_to_api: dict[str, str] = {}
    for option in options:
        base = api_value_to_ha_state_key(option)
        key = base
        suffix = 2
        while key in ha_to_api and ha_to_api[key] != option:
            key = f"{base}_{suffix}"
            suffix += 1
        ha_to_api[key] = option
    api_to_ha = {api: ha for ha, api in ha_to_api.items()}
    return tuple(ha_to_api.keys()), ha_to_api, api_to_ha


@dataclass(frozen=True, slots=True)
class SettingDef:
    """One REST settings key exposed as a Home Assistant entity."""

    key: str
    translation_key: str
    kind: SettingKind
    icon: str
    name_en: str
    name_sv: str
    options: tuple[str, ...] = ()
    min_value: float = 0
    max_value: float = 100
    step: float = 1
    unit: str | None = None


def _enum_options(*values: str) -> tuple[str, ...]:
    return values


# fmt: off
SETTING_DEFS: tuple[SettingDef, ...] = (
    # —— Slideshow ——
    SettingDef("slideshowEnabled", "ss_slideshow", "switch", "mdi:image-multiple", "Slideshow", "Skärmsläckare"),
    SettingDef("slideshowIdleSec", "ss_idle_delay", "number", "mdi:timer-sand", "Slideshow · Idle delay", "Skärmsläckare · Väntetid", min_value=1, max_value=600, step=1, unit="s"),
    SettingDef("slideshowImageSec", "ss_image_duration", "number", "mdi:image-clock", "Slideshow · Image duration", "Skärmsläckare · Bildtid", min_value=3, max_value=120, step=1, unit="s"),
    SettingDef("slideshowClockMode", "ss_clock_mode", "select", "mdi:clock-outline", "Slideshow · Clock mode", "Skärmsläckare · Klockläge", options=_enum_options("images_only", "clock_only", "images_with_clock")),
    SettingDef("slideshowClockOnlyStyle", "ss_clock_style", "select", "mdi:clock-digital", "Slideshow · Clock style", "Skärmsläckare · Klockstil", options=_enum_options("analog", "digital", "digital_v2")),
    SettingDef("slideshowFitMode", "ss_fit_mode", "select", "mdi:fit-to-screen", "Slideshow · Image fit", "Skärmsläckare · Bildpassning", options=_enum_options("cover", "contain")),
    SettingDef("slideshowClockVertical", "ss_clock_vertical", "select", "mdi:arrow-up-down", "Slideshow · Clock vertical", "Skärmsläckare · Klocka vertikalt", options=_enum_options("top", "bottom")),
    SettingDef("slideshowClockHorizontal", "ss_clock_horizontal", "select", "mdi:arrow-left-right", "Slideshow · Clock horizontal", "Skärmsläckare · Klocka horisontellt", options=_enum_options("left", "right")),
    SettingDef("slideshowClockColor", "ss_clock_color", "text", "mdi:palette", "Slideshow · Clock color", "Skärmsläckare · Klockfärg"),
    SettingDef("slideshowClockColorAnalog", "ss_clock_color_analog", "text", "mdi:palette", "Slideshow · Analog clock color", "Skärmsläckare · Analog klockfärg"),
    SettingDef("slideshowClockColorDigital", "ss_clock_color_digital", "text", "mdi:palette", "Slideshow · Digital clock color", "Skärmsläckare · Digital klockfärg"),
    SettingDef("slideshowClockOverlayUseSelectedColor", "ss_clock_overlay_color", "switch", "mdi:palette-swatch", "Slideshow · Clock overlay uses color", "Skärmsläckare · Klocka använder färg"),
    SettingDef("slideshowClockOverlaySize", "ss_clock_overlay_size", "select", "mdi:resize", "Slideshow · Clock overlay size", "Skärmsläckare · Klockstorlek", options=_enum_options("default", "large")),
    SettingDef("slideshowShowDate", "ss_show_date", "switch", "mdi:calendar", "Slideshow · Show date", "Skärmsläckare · Visa datum"),
    SettingDef("slideshowWeatherMode", "ss_weather_mode", "select", "mdi:weather-partly-cloudy", "Slideshow · Weather", "Skärmsläckare · Väder", options=_enum_options("off", "color", "mono")),
    SettingDef("slideshowNightModeEnabled", "ss_night_mode", "switch", "mdi:weather-night", "Slideshow · Night mode", "Skärmsläckare · Nattläge"),
    SettingDef("slideshowNightModeFrom", "ss_night_from", "text", "mdi:clock-start", "Slideshow · Night mode from", "Skärmsläckare · Nattläge från"),
    SettingDef("slideshowNightModeTo", "ss_night_to", "text", "mdi:clock-end", "Slideshow · Night mode to", "Skärmsläckare · Nattläge till"),
    SettingDef("slideshowShowClock", "ss_show_clock", "switch", "mdi:clock", "Slideshow · Show clock", "Skärmsläckare · Visa klocka"),
    SettingDef("slideshowClockOverlay", "ss_clock_overlay", "switch", "mdi:clock-plus", "Slideshow · Clock overlay", "Skärmsläckare · Klocka ovanpå bild"),
    SettingDef("slideshowDigitalClockV2", "ss_digital_clock_v2", "switch", "mdi:clock-digital", "Slideshow · Digital clock v2", "Skärmsläckare · Digital klocka v2"),

    # —— Music appearance ——
    SettingDef("styleMode", "music_style_mode", "select", "mdi:palette-swatch", "Music · Style mode", "Musik · Stil", options=_enum_options("advanced", "simple", "basic", "custom1", "custom2", "custom3")),
    SettingDef("backdropMode", "music_backdrop", "select", "mdi:image-filter-hdr", "Music · Backdrop", "Musik · Bakgrundsbild", options=_enum_options("off", "simple", "original", "fancy")),
    SettingDef("fullscreenAnimation", "music_fullscreen_animation", "select", "mdi:album", "Music · Full-screen animation", "Musik · Helskärmsanimation", options=_enum_options("off", "vinyl", "micVu", "vintageEqBars")),
    SettingDef("micVuDisplayGain", "music_mic_vu_gain", "select", "mdi:microphone", "Music · Mic VU sensitivity", "Musik · VU-känslighet", options=_enum_options("gain1", "gain1_4", "gain1_7")),
    SettingDef("vintageEqDisplayGain", "music_vintage_eq_gain", "select", "mdi:equalizer", "Music · Vintage EQ sensitivity", "Musik · Vintage EQ-känslighet", options=_enum_options("gain1", "gain1_4", "gain1_7")),
    SettingDef("albumCoverStyle", "music_album_cover_style", "select", "mdi:record-player", "Music · Album cover style", "Musik · Albumomslag stil", options=_enum_options("default", "vinylAnimation")),
    SettingDef("vizEqStyle", "music_eq_style", "select", "mdi:waveform", "Music · EQ style", "Musik · EQ-stil", options=_enum_options("off", "naturalWaveColor", "naturalWave")),
    SettingDef("vizEqMode", "music_eq_mode", "select", "mdi:waveform", "Music · EQ mode", "Musik · EQ-läge", options=_enum_options("liveMic", "fake")),
    SettingDef("vizEqSize", "music_eq_size", "select", "mdi:resize", "Music · EQ size", "Musik · EQ-storlek", options=_enum_options("default", "plus40", "plus60")),
    SettingDef("vizEqAlign", "music_eq_align", "select", "mdi:format-horizontal-align-left", "Music · EQ alignment", "Musik · EQ-justering", options=_enum_options("left", "right")),
    SettingDef("metadataTextSize", "music_metadata_size", "select", "mdi:format-size", "Music · Metadata text size", "Musik · Textstorlek", options=_enum_options("off", "minus25", "minus15", "default", "plus10", "plus25", "plus35", "plus45")),
    SettingDef("metadataTextAlign", "music_metadata_align", "select", "mdi:format-align-left", "Music · Metadata alignment", "Musik · Textjustering", options=_enum_options("left", "right")),
    SettingDef("metadataTextVerticalOffset", "music_metadata_vertical", "select", "mdi:format-vertical-align-center", "Music · Metadata vertical offset", "Musik · Text vertikal offset", options=_enum_options("down4", "down3", "down2", "down1", "default", "up1", "up2", "up3", "up4", "up5", "up6", "up7", "up8", "up9", "up10", "up11", "up12")),
    SettingDef("musicTitleMarqueeEnabled", "music_title_marquee", "switch", "mdi:text-box", "Music · Scrolling title", "Musik · Rullande titel"),
    SettingDef("musicTextShadowEnabled", "music_text_shadow", "switch", "mdi:format-text", "Music · Text shadow", "Musik · Textskugga"),
    SettingDef("musicBottomScrimEnabled", "music_bottom_scrim", "switch", "mdi:gradient-vertical", "Music · Bottom scrim", "Musik · Nedre gradient"),
    SettingDef("musicCoverShadowEnabled", "music_cover_shadow", "switch", "mdi:box-shadow", "Music · Cover shadow", "Musik · Omslagsskugga"),
    SettingDef("metadataTitleColor", "music_title_color", "text", "mdi:palette", "Music · Title color", "Musik · Titelfärg"),
    SettingDef("metadataArtistColor", "music_artist_color", "text", "mdi:palette", "Music · Artist color", "Musik · Artistfärg"),
    SettingDef("coverArtCorner", "music_cover_corner", "select", "mdi:album", "Music · Cover corner", "Musik · Omslag hörn", options=_enum_options("left", "right")),
    SettingDef("coverArtSize", "music_cover_size", "select", "mdi:resize", "Music · Cover size", "Musik · Omslagsstorlek", options=_enum_options("off", "minus50", "minus40", "min", "small", "default", "large", "max")),
    SettingDef("showNowPlayingZoneLabelMusic", "music_zone_label", "select", "mdi:speaker", "Music · Zone label", "Musik · Zonetikett", options=_enum_options("off", "on", "bigger")),
    SettingDef("showNowPlayingProgressBarMusic", "music_progress_bar", "select", "mdi:progress-clock", "Music · Progress bar", "Musik · Förloppsindikator", options=_enum_options("off", "on", "blue")),
    SettingDef("youtubePlayMusicVideo", "music_youtube_mv", "switch", "mdi:youtube", "Music · YouTube music video", "Musik · YouTube musikvideo"),

    # —— Video appearance ——
    SettingDef("vizVideoStyleMode", "video_style_mode", "select", "mdi:television", "Video · Theme", "Video · Tema", options=_enum_options("simple", "advanced")),
    SettingDef("appleTvBackdropFitMode", "video_backdrop_fit", "select", "mdi:fit-to-screen", "Video · Backdrop fit", "Video · Bakgrundspassning", options=_enum_options("cover", "contain")),
    SettingDef("vizVideoMetadataTextSize", "video_metadata_size", "select", "mdi:format-size", "Video · Metadata text size", "Video · Textstorlek", options=_enum_options("minus25", "minus15", "default", "plus10", "plus25", "plus35", "plus45")),
    SettingDef("vizVideoMetadataTextAlign", "video_metadata_align", "select", "mdi:format-align-left", "Video · Metadata alignment", "Video · Textjustering", options=_enum_options("left", "right")),
    SettingDef("vizVideoMetadataTextVerticalOffset", "video_metadata_vertical", "select", "mdi:format-vertical-align-center", "Video · Metadata vertical offset", "Video · Text vertikal offset", options=_enum_options("down3", "down2", "down1", "default", "up1", "up2", "up3")),
    SettingDef("videoTitleMarqueeEnabled", "video_title_marquee", "switch", "mdi:text-box", "Video · Scrolling title", "Video · Rullande titel"),
    SettingDef("videoBottomScrimEnabled", "video_bottom_scrim", "switch", "mdi:gradient-vertical", "Video · Bottom scrim", "Video · Nedre gradient"),
    SettingDef("vizVideoShowAppLogo", "video_show_logo", "switch", "mdi:apple", "Video · Show app logo", "Video · Visa applogotyp"),
    SettingDef("showNowPlayingZoneLabelVideo", "video_zone_label", "select", "mdi:speaker", "Video · Zone label", "Video · Zonetikett", options=_enum_options("off", "on", "bigger")),
    SettingDef("showNowPlayingProgressBarVideo", "video_progress_bar", "select", "mdi:progress-clock", "Video · Progress bar", "Video · Förloppsindikator", options=_enum_options("off", "on", "blue")),
    SettingDef("vizVideoMetadataTitleColor", "video_title_color", "text", "mdi:palette", "Video · Title color", "Video · Titelfärg"),
    SettingDef("vizVideoMetadataOtherTextColor", "video_other_text_color", "text", "mdi:palette", "Video · Other text color", "Video · Övrig textfärg"),

    # —— Display area (basic) ——
    SettingDef("displayAreaInsetHorizontalPct", "display_inset_horizontal", "number", "mdi:arrow-expand-horizontal", "Display · Horizontal underscan", "Visningsyta · Horisontell underskanning", min_value=0, max_value=40, step=1, unit="%"),
    SettingDef("displayAreaInsetVerticalPct", "display_inset_vertical", "number", "mdi:arrow-expand-vertical", "Display · Vertical underscan", "Visningsyta · Vertikal underskanning", min_value=0, max_value=40, step=1, unit="%"),

    # —— Misc (basic UI) ——
    SettingDef("statusPanelMode", "misc_status_panel", "select", "mdi:information-outline", "Status panel", "Statuspanel", options=_enum_options("statusBar", "panel", "off")),
    SettingDef("idleStatusHudAutoHideSec", "misc_hud_auto_hide", "number", "mdi:eye-off", "HUD auto-hide delay", "Tid innan GUI döljs", min_value=0, max_value=120, step=1, unit="s"),
    SettingDef("immersiveSystemUi", "misc_immersive_ui", "switch", "mdi:fullscreen", "Immersive system UI", "Helskärmsläge (system-UI)"),
    SettingDef("hideIdleAppBackground", "misc_hide_idle_bg", "switch", "mdi:rectangle-outline", "Hide idle background", "Dölj bakgrund i viloläge"),
    SettingDef("osdControlsEnabled", "misc_osd_controls", "switch", "mdi:gesture-tap", "OSD controls", "OSD-kontroller"),
    SettingDef("androidAutostartOnBoot", "misc_autostart", "switch", "mdi:restart", "Autostart on boot", "Starta vid uppstart"),
    SettingDef("setupAutoCloseSec", "misc_setup_auto_close", "number", "mdi:timer-outline", "Setup auto-close", "Setup stängs automatiskt", min_value=0, max_value=600, step=1, unit="s"),

    # —— Adaptive brightness ——
    SettingDef("adaptiveBrightnessEnabled", "lux_enabled", "switch", "mdi:brightness-auto", "Adaptive brightness", "Adaptiv ljusstyrka"),
    SettingDef("adaptiveBrightnessRange1Percent", "lux_range_1", "number", "mdi:brightness-1", "Brightness · 0–7 lux", "Ljusstyrka · 0–7 lux", min_value=0, max_value=100, step=1, unit="%"),
    SettingDef("adaptiveBrightnessRange2Percent", "lux_range_2", "number", "mdi:brightness-2", "Brightness · 8–50 lux", "Ljusstyrka · 8–50 lux", min_value=0, max_value=100, step=1, unit="%"),
    SettingDef("adaptiveBrightnessRange3Percent", "lux_range_3", "number", "mdi:brightness-3", "Brightness · 51–200 lux", "Ljusstyrka · 51–200 lux", min_value=0, max_value=100, step=1, unit="%"),
    SettingDef("adaptiveBrightnessRange4Percent", "lux_range_4", "number", "mdi:brightness-4", "Brightness · 201–500 lux", "Ljusstyrka · 201–500 lux", min_value=0, max_value=100, step=1, unit="%"),
    SettingDef("adaptiveBrightnessRange5Percent", "lux_range_5", "number", "mdi:brightness-5", "Brightness · 500+ lux", "Ljusstyrka · 500+ lux", min_value=0, max_value=100, step=1, unit="%"),

    # —— Integration enable toggles only ——
    SettingDef("roonEnabled", "integ_roon", "switch", "mdi:music-circle", "Integration · Roon", "Integration · Roon"),
    SettingDef("appleTvEnabled", "integ_apple_tv", "switch", "mdi:apple", "Integration · Apple TV", "Integration · Apple TV"),
    SettingDef("musicIdEnabled", "integ_musicid", "switch", "mdi:ear-hearing", "Integration · Lyssna själv", "Integration · Lyssna själv"),
    SettingDef("googleDevicesEnabled", "integ_google_cast", "switch", "mdi:cast", "Integration · Google Cast", "Integration · Google Cast"),
    SettingDef("spotifyEnabled", "integ_spotify", "switch", "mdi:spotify", "Integration · Spotify", "Integration · Spotify"),
    SettingDef("afterburnerEnabled", "integ_afterburner", "switch", "mdi:chart-line", "Integration · MSI Afterburner", "Integration · MSI Afterburner"),
    SettingDef("experimentalWiimEnabled", "integ_wiim", "switch", "mdi:speaker-wireless", "Integration · WiiM", "Integration · WiiM"),
    SettingDef("experimentalNaimEnabled", "integ_naim", "switch", "mdi:speaker", "Integration · NAIM", "Integration · NAIM"),
    SettingDef("experimentalEversoloEnabled", "integ_eversolo", "switch", "mdi:speaker", "Integration · Eversolo", "Integration · Eversolo"),
    SettingDef("youtubeEnabled", "integ_youtube", "switch", "mdi:youtube", "Integration · YouTube", "Integration · YouTube"),
    SettingDef("musicIdShowMicIndicator", "integ_musicid_mic_indicator", "switch", "mdi:microphone", "Lyssna · Show mic indicator", "Lyssna · Visa mic-indikator"),
    SettingDef("youtubeShowPlayingBadge", "integ_youtube_badge", "switch", "mdi:badge-account", "YouTube · Playing badge", "YouTube · Spelar-märke"),
)
# fmt: on

SETTING_DEFS_BY_KEY: dict[str, SettingDef] = {d.key: d for d in SETTING_DEFS}
SETTING_DEFS_BY_KIND: dict[SettingKind, tuple[SettingDef, ...]] = {
    "switch": tuple(d for d in SETTING_DEFS if d.kind == "switch"),
    "select": tuple(d for d in SETTING_DEFS if d.kind == "select"),
    "number": tuple(d for d in SETTING_DEFS if d.kind == "number"),
    "text": tuple(d for d in SETTING_DEFS if d.kind == "text"),
}

# Select option labels for strings.json / translations (EN).
SELECT_STATE_LABELS_EN: dict[str, dict[str, str]] = {
    "slideshowClockMode": {"images_only": "Images only", "clock_only": "Clock only", "images_with_clock": "Images with clock"},
    "slideshowClockOnlyStyle": {"analog": "Analog", "digital": "Digital", "digital_v2": "Digital v2"},
    "slideshowFitMode": {"cover": "Fill (cover)", "contain": "Fit (contain)"},
    "slideshowClockVertical": {"top": "Top", "bottom": "Bottom"},
    "slideshowClockHorizontal": {"left": "Left", "right": "Right"},
    "slideshowClockOverlaySize": {"default": "Default", "large": "Large"},
    "slideshowWeatherMode": {"off": "Off", "color": "Color", "mono": "Monochrome"},
    "styleMode": {"advanced": "Modern", "simple": "Basic", "basic": "Minimal", "custom1": "Custom 1", "custom2": "Custom 2", "custom3": "Custom 3"},
    "backdropMode": {"off": "Off", "simple": "Standard", "original": "Original", "fancy": "Fancy"},
    "fullscreenAnimation": {"off": "Off", "vinyl": "Vinyl", "micVu": "Mic VU", "vintageEqBars": "Vintage EQ bars"},
    "albumCoverStyle": {"default": "Default", "vinylAnimation": "Animated"},
    "micVuDisplayGain": {"gain1": "×1", "gain1_4": "×1.4", "gain1_7": "×1.7"},
    "vintageEqDisplayGain": {"gain1": "×1", "gain1_4": "×1.4", "gain1_7": "×1.7"},
    "vizEqAlign": {"left": "Left", "right": "Right"},
    "vizEqSize": {"default": "Default", "plus40": "+40%", "plus60": "+60%"},
    "vizEqStyle": {"off": "Off", "naturalWaveColor": "Colored", "naturalWave": "Standard"},
    "vizEqMode": {"liveMic": "Live mic", "fake": "Fake"},
    "metadataTextSize": {"off": "Off", "minus25": "−25%", "minus15": "−15%", "default": "Default", "plus10": "+10%", "plus25": "+25%", "plus35": "+35%", "plus45": "+45%"},
    "metadataTextAlign": {"left": "Left", "right": "Right"},
    "metadataTextVerticalOffset": {"default": "0", "up1": "1", "up2": "2", "up3": "3", "up4": "4", "up5": "5", "up6": "6", "up7": "7", "up8": "8", "up9": "9", "up10": "10", "up11": "11", "up12": "12", "down1": "−1", "down2": "−2", "down3": "−3", "down4": "−4"},
    "showNowPlayingZoneLabelMusic": {"off": "Off", "on": "On", "bigger": "Larger"},
    "showNowPlayingProgressBarMusic": {"off": "Off", "on": "On", "blue": "Blue"},
    "showNowPlayingProgressBarVideo": {"off": "Off", "on": "On", "blue": "Blue"},
    "coverArtCorner": {"left": "Left", "right": "Right"},
    "coverArtSize": {"off": "Off", "minus50": "−50%", "minus40": "−40%", "min": "−30%", "small": "−20%", "default": "0%", "large": "+20%", "max": "+30%"},
    "vizVideoStyleMode": {"simple": "Basic", "advanced": "Modern"},
    "appleTvBackdropFitMode": {"cover": "Fill (cover)", "contain": "Fit (contain)"},
    "vizVideoMetadataTextSize": {"minus25": "−25%", "minus15": "−15%", "default": "Default", "plus10": "+10%", "plus25": "+25%", "plus35": "+35%", "plus45": "+45%"},
    "vizVideoMetadataTextAlign": {"left": "Left", "right": "Right"},
    "vizVideoMetadataTextVerticalOffset": {"default": "0", "up1": "1", "up2": "2", "up3": "3", "down1": "−1", "down2": "−2", "down3": "−3"},
    "showNowPlayingZoneLabelVideo": {"off": "Off", "on": "On", "bigger": "Larger"},
    "statusPanelMode": {"statusBar": "Status bar", "panel": "Panel", "off": "Off"},
}

SELECT_STATE_LABELS_SV: dict[str, dict[str, str]] = {
    "slideshowClockMode": {"images_only": "Bilder", "clock_only": "Klocka", "images_with_clock": "Bilder med klocka"},
    "slideshowClockOnlyStyle": {"analog": "Analog", "digital": "Digital", "digital_v2": "Digital v2"},
    "slideshowFitMode": {"cover": "Fyll", "contain": "Passa in"},
    "slideshowClockVertical": {"top": "Upptill", "bottom": "Nertill"},
    "slideshowClockHorizontal": {"left": "Vänster", "right": "Höger"},
    "slideshowClockOverlaySize": {"default": "Standard", "large": "Större"},
    "slideshowWeatherMode": {"off": "Av", "color": "På", "mono": "Svart/vit"},
    "styleMode": {"advanced": "Modern", "simple": "Basic", "basic": "Minimal", "custom1": "Egen 1", "custom2": "Egen 2", "custom3": "Egen 3"},
    "backdropMode": {"off": "Av", "simple": "Standard", "original": "Original", "fancy": "Fancy"},
    "fullscreenAnimation": {"off": "Av", "vinyl": "Vinyl", "micVu": "Mic VU", "vintageEqBars": "Vintage EQ"},
    "albumCoverStyle": {"default": "Standard", "vinylAnimation": "Animerad"},
    "micVuDisplayGain": {"gain1": "×1", "gain1_4": "×1,4", "gain1_7": "×1,7"},
    "vintageEqDisplayGain": {"gain1": "×1", "gain1_4": "×1,4", "gain1_7": "×1,7"},
    "vizEqAlign": {"left": "Vänster", "right": "Höger"},
    "vizEqSize": {"default": "Standard", "plus40": "+40%", "plus60": "+60%"},
    "vizEqStyle": {"off": "Av", "naturalWaveColor": "Färgade", "naturalWave": "Standard"},
    "vizEqMode": {"liveMic": "Live mic", "fake": "Fake"},
    "metadataTextSize": {"off": "Av", "minus25": "−25%", "minus15": "−15%", "default": "Standard", "plus10": "+10%", "plus25": "+25%", "plus35": "+35%", "plus45": "+45%"},
    "metadataTextAlign": {"left": "Vänster", "right": "Höger"},
    "metadataTextVerticalOffset": {"default": "0", "up1": "1", "up2": "2", "up3": "3", "up4": "4", "up5": "5", "up6": "6", "up7": "7", "up8": "8", "up9": "9", "up10": "10", "up11": "11", "up12": "12", "down1": "−1", "down2": "−2", "down3": "−3", "down4": "−4"},
    "showNowPlayingZoneLabelMusic": {"off": "Av", "on": "På", "bigger": "Större"},
    "showNowPlayingProgressBarMusic": {"off": "Av", "on": "På", "blue": "Blå"},
    "showNowPlayingProgressBarVideo": {"off": "Av", "on": "På", "blue": "Blå"},
    "coverArtCorner": {"left": "Vänster", "right": "Höger"},
    "coverArtSize": {"off": "Av", "minus50": "−50%", "minus40": "−40%", "min": "−30%", "small": "−20%", "default": "0%", "large": "+20%", "max": "+30%"},
    "vizVideoStyleMode": {"simple": "Basic", "advanced": "Modern"},
    "appleTvBackdropFitMode": {"cover": "Fyll", "contain": "Passa in"},
    "vizVideoMetadataTextSize": {"minus25": "−25%", "minus15": "−15%", "default": "Standard", "plus10": "+10%", "plus25": "+25%", "plus35": "+35%", "plus45": "+45%"},
    "vizVideoMetadataTextAlign": {"left": "Vänster", "right": "Höger"},
    "vizVideoMetadataTextVerticalOffset": {"default": "0", "up1": "1", "up2": "2", "up3": "3", "down1": "−1", "down2": "−2", "down3": "−3"},
    "showNowPlayingZoneLabelVideo": {"off": "Av", "on": "På", "bigger": "Större"},
    "statusPanelMode": {"statusBar": "Statusrad", "panel": "Panel", "off": "Av"},
}
