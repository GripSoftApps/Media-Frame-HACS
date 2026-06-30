# Media Frame — Home Assistant integration (HACS)

Official-style custom component for the **Media Frame** Android tablet app. It talks to the same LAN REST API as **Web control** in Setup and the browser Setup GUI (`setup-web.html` on port **8787**).

## Requirements

- Home Assistant **2024.6** or newer
- Media Frame on Android with **Web control** enabled in Setup (one toggle — starts both the web GUI and the REST API)
- Tablet and Home Assistant on the same LAN (LAN-only by default)

## Enable Web control on the tablet

1. Open **Setup** → **Web control** (own item in the main hub menu — not under Connected apps)
2. Turn **Enable / disable** on
3. Set a **password** (minimum 4 characters) — use the same value as the Bearer token in Home Assistant
4. Note the **TCP port** (default **8787**) and the tablet **LAN IP** (shown on the same screen)

Play Store installs ship with Web control **off** by default; you must enable it manually.

## Install via HACS

1. In HACS → **Integrations** → **Custom repositories**
2. Add this repository URL and category **Integration**
3. Install **Media Frame**
4. Restart Home Assistant
5. **Settings → Devices & services → Add integration → Media Frame**
6. Enter host, port, and token

### Manual install

Copy `custom_components/media_frame/` into your Home Assistant `config/custom_components/` folder and restart.

## What you get (v2)

Each entity has a **descriptive name** (e.g. *Music · Full-screen animation*, *Slideshow · Idle delay*) — not just the tablet device name.

| Platform | Purpose |
|----------|---------|
| **Switch** | Slideshow, integration on/off, appearance toggles |
| **Select** | Music/video appearance enums (backdrop, vinyl animation, EQ, metadata, …) |
| **Number** | Slideshow timers, display underscan, adaptive brightness ranges |
| **Text** | Slideshow clock colors, metadata colors, night-mode times |
| **Sensor** | App version, battery %, CPU %, Roon zone count, Lyssna mic level |
| **Binary sensor** | REST online, slideshow active, integration connection status |
| **Services** | `media_frame.patch_settings` (advanced), `media_frame.call_action` (power users) |

**Not included:** connection/pairing flows (Roon connect, Cast discover, Lyssna listen-now), transport controls (Roon play/pause), remember-last-played, or deep Setup keys (hosts, tokens, ports).

Polling interval: **30 seconds** (health + integration status snapshots).

After upgrading from v1, remove stale entities in **Settings → Devices & services → Media Frame → Entities** (old buttons/switches) or reload the integration.

## Services

### `media_frame.patch_settings`

Patch any allowed setting key (same allowlist as `remoteRestPatch.js` / `PATCH_KEYS`):

```yaml
service: media_frame.patch_settings
data:
  entity_id: sensor.media_frame_battery
  patch:
    fullscreenAnimation: vinyl
    backdropMode: fancy
```

### `media_frame.call_action`

Low-level POST to `/api/v1/` (for automation authors; most users should use entities instead):

```yaml
service: media_frame.call_action
data:
  entity_id: sensor.media_frame_battery
  action: system/restartApp
```

## Play Store compatibility

See [PLAYSTORE.md](PLAYSTORE.md). Summary:

- **REST works** on Play Store builds (same `LocalRestControlModule`)
- REST is **disabled by default** until the user turns it on
- Core HA features (health, settings, appearance, slideshow, integration toggles) are **supported**
- Blocked on Play Store only: debug logs, YouTube REST, OTA `updateApp`, kiosk unlock/PIN

## Development

Entity catalog: `ha_settings.py`. Regenerate translation files after catalog edits:

```bash
python custom_components/media_frame/gen_translations.py
```

This integration lives in the main Media Frame monorepo:

```
custom_components/media_frame/
hacs.json
```

Point HACS at the GitHub repository root; `custom_components/media_frame` is discovered automatically.

## License

Same license as the Media Frame project.
