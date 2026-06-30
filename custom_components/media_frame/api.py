"""HTTP client for the Media Frame tablet LAN REST API."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import aiohttp

from .const import API_PREFIX, DEFAULT_PORT

_LOGGER = logging.getLogger(__name__)

ACTION_POLL_INTERVAL = 0.4
ACTION_POLL_MAX_ATTEMPTS = 30


class MediaFrameApiError(Exception):
    """Base API error."""


class MediaFrameAuthError(MediaFrameApiError):
    """401 / missing or invalid token."""


class MediaFrameConnectionError(MediaFrameApiError):
    """Host unreachable or REST disabled."""


class MediaFrameApi:
    """Thin async wrapper around Media Frame REST (port 8787 by default)."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        token: str,
        port: int = DEFAULT_PORT,
    ) -> None:
        self._session = session
        self._host = host.strip()
        self._port = int(port)
        self._token = token.strip()
        self._base = f"http://{self._host}:{self._port}{API_PREFIX}"

    @property
    def base_url(self) -> str:
        """REST base including /api/v1."""
        return self._base

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "X-Media-Frame-Rest-Token": self._token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
    ) -> Any:
        url = f"{self._base}{path}"
        try:
            async with self._session.request(
                method,
                url,
                headers=self._headers(),
                json=json_body,
                params=params,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                text = await resp.text()
                if resp.status == 401:
                    raise MediaFrameAuthError("unauthorized")
                if resp.status >= 400:
                    raise MediaFrameApiError(f"HTTP {resp.status}: {text[:200]}")
                if not text:
                    return {}
                try:
                    return json.loads(text)
                except ValueError as err:
                    raise MediaFrameApiError(f"invalid JSON from {path}") from err
        except aiohttp.ClientError as err:
            raise MediaFrameConnectionError(str(err)) from err

    async def validate(self) -> dict[str, Any]:
        """Ping health endpoint; raises on failure."""
        return await self.get_health()

    async def get_health(self) -> dict[str, Any]:
        return await self._request("GET", "/health")

    async def get_group_identity(self) -> dict[str, Any]:
        return await self._request("GET", "/group/identity")

    async def get_settings(self) -> dict[str, Any]:
        return await self._request("GET", "/settings")

    async def patch_settings(self, patch: dict[str, Any]) -> dict[str, Any]:
        return await self._request("POST", "/settings", json_body=patch)

    async def get_integration_status(self, name: str) -> dict[str, Any]:
        return await self._request("GET", f"/{name}/status")

    async def get_roon_zones(self) -> dict[str, Any]:
        return await self._request("GET", "/roon/zones")

    async def get_group_status(self) -> dict[str, Any]:
        return await self._request("GET", "/group/status")

    async def post_action(self, op: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        """POST /api/v1/{op} — op is path after /api/v1/ (e.g. roon/transport)."""
        path = f"/{op}" if op.startswith("/") else f"/{op}"
        return await self._request("POST", path, json_body=body or {})

    async def get_action_result(self, action_id: str) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/integration/action-result",
            params={"id": action_id},
        )

    async def post_action_and_wait(
        self,
        op: str,
        body: dict[str, Any] | None = None,
        *,
        max_attempts: int = ACTION_POLL_MAX_ATTEMPTS,
    ) -> dict[str, Any]:
        """Enqueue action and poll until result is no longer pending."""
        accepted = await self.post_action(op, body)
        action_id = str(accepted.get("id", "")).strip()
        if not action_id:
            return accepted
        for _ in range(max_attempts):
            result = await self.get_action_result(action_id)
            err = str(result.get("error", ""))
            if err and err not in ("result_pending",):
                return result
            if result.get("ok") is True and err != "result_pending":
                return result
            if result.get("status") not in (None, "in_progress", "pending"):
                return result
            await asyncio.sleep(ACTION_POLL_INTERVAL)
        return {"ok": False, "error": "action_timeout", "id": action_id}
