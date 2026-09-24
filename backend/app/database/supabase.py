from typing import Any

import httpx

from app.core.config import get_settings
from app.core.exceptions import SupabaseError


class SupabaseGateway:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _key(self, elevated: bool = False) -> str:
        if elevated and self.settings.supabase_secret_key:
            return self.settings.supabase_secret_key
        return self.settings.supabase_publishable_key

    def _headers(self, token: str | None = None, elevated: bool = False) -> dict[str, str]:
        key = self._key(elevated)
        if not self.settings.supabase_configured:
            raise SupabaseError(
                "Supabase ainda não foi configurado no servidor.",
                status_code=503,
                code="supabase_not_configured",
            )
        return {
            "apikey": key,
            "Authorization": f"Bearer {token or key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def request(
        self,
        method: str,
        path: str,
        *,
        token: str | None = None,
        params: dict[str, Any] | None = None,
        payload: Any = None,
        elevated: bool = False,
        prefer: str | None = None,
    ) -> Any:
        headers = self._headers(token, elevated)
        if prefer:
            headers["Prefer"] = prefer

        async with httpx.AsyncClient(base_url=self.settings.supabase_url, timeout=20) as client:
            response = await client.request(method, path, headers=headers, params=params, json=payload)

        if response.status_code >= 400:
            try:
                detail = response.json()
                message = detail.get("msg") or detail.get("message") or detail.get("error_description") or detail.get("error")
            except ValueError:
                message = response.text
            raise SupabaseError(
                message or "Falha ao acessar o Supabase.",
                status_code=response.status_code if response.status_code < 500 else 502,
                code="supabase_request_failed",
            )

        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    async def get_user(self, token: str) -> dict[str, Any]:
        return await self.request("GET", "/auth/v1/user", token=token)

    async def select(self, table: str, token: str, **params: Any) -> list[dict[str, Any]]:
        return await self.request("GET", f"/rest/v1/{table}", token=token, params=params)

    async def insert(
        self, table: str, payload: dict[str, Any], token: str | None, *, elevated: bool = False
    ) -> dict[str, Any]:
        rows = await self.request(
            "POST", f"/rest/v1/{table}", token=token, payload=payload,
            elevated=elevated, prefer="return=representation"
        )
        return rows[0] if rows else {}

    async def update(
        self, table: str, payload: dict[str, Any], token: str, **filters: Any
    ) -> dict[str, Any]:
        rows = await self.request(
            "PATCH", f"/rest/v1/{table}", token=token, params=filters,
            payload=payload, prefer="return=representation"
        )
        return rows[0] if rows else {}

    async def rpc(self, function: str, payload: dict[str, Any], token: str) -> Any:
        return await self.request("POST", f"/rest/v1/rpc/{function}", token=token, payload=payload)


gateway = SupabaseGateway()
