# Media Frame — Home Assistant (HACS)

Home Assistant custom integration for the [**Media Frame**](https://github.com/GripSoftApps/Media-Frame) Android tablet app. Controls and monitors your tablet over the same LAN REST API as **Web control** in the app Setup.

[![Validate](https://github.com/GripSoftApps/Media-Frame-HACS/actions/workflows/validate.yaml/badge.svg)](https://github.com/GripSoftApps/Media-Frame-HACS/actions/workflows/validate.yaml)

## Quick install (HACS)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=GripSoftApps&repository=Media-Frame-HACS&category=integration)

1. HACS → **Integrations** → **Custom repositories** → add `https://github.com/GripSoftApps/Media-Frame-HACS` (category **Integration**)
2. Install **Media Frame** → restart Home Assistant
3. **Settings → Devices & services → Add integration → Media Frame**
4. Enter tablet **IP**, **port** (default `8787`), and your **password** (same as Setup → Web control)

### Enable Web control on the tablet

1. Setup → **Web control** (own item in the main hub menu — not under Connected apps)
2. Turn **Enable / disable** on
3. Set a **password** (minimum **4 characters**) and save
4. Tablet and Home Assistant must be on the same LAN

Play Store builds ship with Web control **off** until you enable it. See [PLAYSTORE.md](custom_components/media_frame/PLAYSTORE.md).

## Features

| Platform | Examples |
|----------|----------|
| **Sensor** | App version, battery, CPU, Roon zones, Lyssna mic level |
| **Binary sensor** | REST online, slideshow, Roon / Apple TV / Cast / Lyssna |
| **Switch** | Slideshow, Roon, Apple TV, Lyssna, Google Cast |
| **Number** | Slideshow idle / image duration |
| **Button** | Roon connect, play/pause, Lyssna now, Cast discover, restart app |
| **Services** | `media_frame.patch_settings`, `media_frame.call_action` |

## Example automation

```yaml
service: media_frame.patch_settings
target:
  entity_id: sensor.media_frame_battery
data:
  patch:
    slideshowEnabled: true
    slideshowIdleSec: 120
```

```yaml
service: media_frame.call_action
target:
  entity_id: button.media_frame_roon_pause
data:
  action: roon/transport
  body:
    control: pause
```

## Manual install

Copy `custom_components/media_frame/` into your Home Assistant `config/custom_components/` directory and restart.

## Related repos

| Repo | Purpose |
|------|---------|
| [Media-Frame](https://github.com/GripSoftApps/Media-Frame) | Android tablet app |
| [Media-Frame-Info](https://github.com/GripSoftApps/Media-Frame-Info) | User documentation |

## License

MIT — see [LICENSE](LICENSE).
