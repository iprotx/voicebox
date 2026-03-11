"""Async client for Voicebox local API."""

from __future__ import annotations

from typing import Any

import httpx


class VoiceboxAPIClient:
    """Wrapper around local Voicebox backend API endpoints."""

    def __init__(self, base_url: str = "http://localhost:17493", timeout: float = 20.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()

    async def health(self) -> dict[str, Any]:
        return await self._request("GET", "/health")

    async def list_profiles(self) -> list[dict[str, Any]]:
        return await self._request("GET", "/profiles")

    async def generate(self, profile_id: str, text: str, language: str = "en") -> dict[str, Any]:
        payload = {
            "profile_id": profile_id,
            "text": text,
            "language": language,
        }
        return await self._request("POST", "/generate", json=payload)
