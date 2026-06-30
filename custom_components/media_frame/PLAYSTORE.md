# Play Store vs fleet REST — Home Assistant impact

Verified against `LocalRestControlModule.kt` (`isPlayStoreBlockedRestPath`) and `playStoreSettingsSanitize.js`.

## REST server on Play Store

| Item | Fleet / sideload APK | Google Play APK |
|------|----------------------|-----------------|
| `LocalRestControlModule` present | Yes | Yes |
| Web GUI (`setup-web.html`) | Yes | Yes (playstore asset variant) |
| Default `restControlEnabled` | User choice | **`false`** (must enable in Setup) |
| Auth | Bearer + `X-Media-Frame-Rest-Token` | Same |
| Default port | 8787 | 8787 |
| LAN-only filter | Default on | Default on |
| Token required when server on | ≥ 4 chars | ≥ 4 chars |

**Conclusion:** Play Store **actively supports** the REST API the HA integration uses, but users must **opt in** (enable **Web control** in Setup and set the password).

Group control can also start the HTTP server when `groupControlEnabled` is true even if Web control is off — HA still needs a valid password.

## Endpoints the integration uses

| Endpoint | Play Store | HA integration usage |
|----------|------------|----------------------|
| `GET /api/v1/health` | Allowed | Config validation, sensors |
| `GET /api/v1/settings` | Allowed | Switches, numbers |
| `POST /api/v1/settings` | Allowed | Switches, numbers, `patch_settings` service |
| `GET /api/v1/{integration}/status` | Allowed | Binary sensors (not YouTube) |
| `GET /api/v1/roon/zones` | Allowed | Roon zone count sensor |
| `GET /api/v1/group/*` | Allowed | Device identity (optional) |
| `POST /api/v1/roon/connect` | Allowed | Button |
| `POST /api/v1/roon/transport` | Allowed | Play/pause buttons, service |
| `POST /api/v1/musicid/listenNow` | Allowed | Button |
| `POST /api/v1/googledevices/discover` | Allowed | Button |
| `POST /api/v1/system/restartApp` | Allowed | Button |
| `GET /api/v1/integration/action-result` | Allowed | Action polling |

## Blocked on Play Store (not used by v1 integration)

| Path | Reason |
|------|--------|
| `/api/v1/debug/*` | Debug / felsökning |
| `/api/v1/youtube/*` | YouTube disabled on Play Store |
| `/api/v1/system/updateApp` | OTA sideload only |
| `/api/v1/system/unlock` | Kiosk |
| `/api/v1/system/kioskHardLock*` | Kiosk |
| `/api/v1/diagnostics/uploadCrashLog` | Diagnostics |

## Settings stripped on Play Store (PATCH still safe)

Play Store builds strip YouTube keys from persisted settings. Patching `youtubeEnabled` via HA has no effect on Play Store — by design.

## HA user checklist (Play Store)

1. Install Media Frame from Google Play
2. Setup → **Web control** → turn **Enable / disable** on
3. Set password (save settings)
4. Confirm from a PC on LAN:  
   `curl -H "Authorization: Bearer YOUR_TOKEN" http://TABLET_IP:8787/api/v1/health`
5. Add integration in HA with same host/port/password

If step 4 returns `401`, fix the password/token. If connection refused, Web control is off or wrong port/firewall.
