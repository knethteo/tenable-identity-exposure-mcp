"""HTTP client wrapper for the Tenable Identity Exposure REST API."""

from __future__ import annotations

import os
from typing import Any

import httpx
import structlog

log = structlog.get_logger(__name__)


class TIEConfigError(ValueError):
    pass


class TIEApiError(RuntimeError):
    def __init__(self, status: int, method: str, path: str, body: str) -> None:
        self.status = status
        super().__init__(f"TIE API {method} {path} -> HTTP {status}: {body}")


class TIEConfig:
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        verify_ssl: bool = True,
        timeout: float = 30.0,
        env_prefix: str = "TIE_",
    ) -> None:
        pfx = env_prefix
        self.base_url = (base_url or os.environ.get(f"{pfx}URL", "")).rstrip("/")
        self.api_key = api_key or os.environ.get(f"{pfx}API_KEY", "")
        self.verify_ssl = verify_ssl if verify_ssl is not None else (
            os.environ.get(f"{pfx}VERIFY_SSL", "true").lower() != "false"
        )
        self.timeout = timeout

        if not self.base_url:
            raise TIEConfigError(f"TIE base URL not set. Provide base_url or set {pfx}URL.")
        if not self.api_key:
            raise TIEConfigError(f"TIE API key not set. Provide api_key or set {pfx}API_KEY.")


class TIEClient:
    def __init__(self, config: TIEConfig) -> None:
        self.config = config
        self._http = httpx.AsyncClient(
            base_url=config.base_url,
            headers={
                "X-API-Key": config.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            verify=config.verify_ssl,
            timeout=config.timeout,
        )

    async def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        method = method.upper()
        log.debug("tie_request", method=method, path=path, params=params)

        resp = await self._http.request(method, path, params=params, json=json)

        if not resp.is_success:
            raise TIEApiError(resp.status_code, method, path, resp.text[:500])

        if resp.status_code == 204 or not resp.content:
            return {"status": "ok"}

        ctype = resp.headers.get("content-type", "")
        if "json" in ctype:
            return resp.json()
        # Some endpoints (e.g. /api/metrics) return non-JSON payloads.
        try:
            return resp.json()
        except ValueError:
            return {"content_type": ctype, "text": resp.text}

    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return await self.request("GET", path, params=params)

    async def post(self, path: str, json: dict[str, Any] | None = None) -> Any:
        return await self.request("POST", path, json=json)

    async def patch(self, path: str, json: dict[str, Any] | None = None) -> Any:
        return await self.request("PATCH", path, json=json)

    async def put(self, path: str, json: dict[str, Any] | None = None) -> Any:
        return await self.request("PUT", path, json=json)

    async def delete(self, path: str) -> Any:
        return await self.request("DELETE", path)

    async def close(self) -> None:
        await self._http.aclose()
