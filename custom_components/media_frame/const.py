"""Constants for the Media Frame integration."""

DOMAIN = "media_frame"

CONF_HOST = "host"
CONF_PORT = "port"
CONF_TOKEN = "token"

DEFAULT_PORT = 8787
DEFAULT_SCAN_INTERVAL = 30

API_PREFIX = "/api/v1"

# Integration status keys exposed by GET /api/v1/{name}/status
INTEGRATION_STATUS_KEYS = (
    "roon",
    "appletv",
    "spotify",
    "musicid",
    "googledevices",
    "wiim",
    "naim",
    "eversolo",
)
