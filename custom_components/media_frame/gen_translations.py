"""One-off helper to refresh strings.json entity blocks from ha_settings.py."""

import json
from pathlib import Path

from ha_settings import SELECT_STATE_LABELS_EN, SELECT_STATE_LABELS_SV, SETTING_DEFS

ROOT = Path(__file__).parent


def build_entity_block(lang: str) -> dict:
    if lang == "en":
        entity = {
            "switch": {},
            "select": {},
            "number": {},
            "text": {},
            "sensor": {
                "app_version": {"name": "App version"},
                "battery": {"name": "Battery"},
                "cpu": {"name": "CPU usage"},
                "roon_zones_count": {"name": "Roon zones"},
                "musicid_mic_dbfs": {"name": "Lyssna mic level"},
            },
            "binary_sensor": {
                "rest_online": {"name": "REST online"},
                "slideshow_enabled": {"name": "Slideshow active"},
                "roon_connected": {"name": "Roon connected"},
                "appletv_connected": {"name": "Apple TV connected"},
                "musicid_listening": {"name": "Lyssna active"},
                "google_cast_available": {"name": "Google Cast devices"},
            },
        }
        labels_map = SELECT_STATE_LABELS_EN
        name_attr = "name_en"
    else:
        entity = {
            "switch": {},
            "select": {},
            "number": {},
            "text": {},
            "sensor": {
                "app_version": {"name": "Appversion"},
                "battery": {"name": "Batteri"},
                "cpu": {"name": "CPU-belastning"},
                "roon_zones_count": {"name": "Roon-zoner"},
                "musicid_mic_dbfs": {"name": "Lyssna mic-nivå"},
            },
            "binary_sensor": {
                "rest_online": {"name": "REST online"},
                "slideshow_enabled": {"name": "Skärmsläckare aktiv"},
                "roon_connected": {"name": "Roon ansluten"},
                "appletv_connected": {"name": "Apple TV ansluten"},
                "musicid_listening": {"name": "Lyssna aktiv"},
                "google_cast_available": {"name": "Google Cast-enheter"},
            },
        }
        labels_map = SELECT_STATE_LABELS_SV
        name_attr = "name_sv"

    for definition in SETTING_DEFS:
        block = {"name": getattr(definition, name_attr)}
        if definition.kind == "select":
            labels = labels_map.get(definition.key, {})
            if labels:
                block["state"] = labels
        entity[definition.kind][definition.translation_key] = block
    return entity


def main() -> None:
    strings_path = ROOT / "strings.json"
    strings = json.loads(strings_path.read_text(encoding="utf-8"))
    strings["entity"] = build_entity_block("en")
    strings_path.write_text(json.dumps(strings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    sv_path = ROOT / "translations" / "sv.json"
    sv = json.loads(sv_path.read_text(encoding="utf-8"))
    sv["entity"] = build_entity_block("sv")
    sv_path.write_text(json.dumps(sv, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    en_path = ROOT / "translations" / "en.json"
    en = {"entity": build_entity_block("en")}
    en_path.write_text(json.dumps(en, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("Updated strings.json, translations/sv.json, translations/en.json")


if __name__ == "__main__":
    main()
