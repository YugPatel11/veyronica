"""HTTP-based connector adapter base.

Shared HTTP client logic for ERP, LMS, CRM adapters.
"""

from __future__ import annotations

import time
from typing import Any

import httpx
import structlog

from app.connectors import (
    BaseConnector,
    ConnectorResult,
    ConnectorStatus,
    DiffChange,
    DiffResult,
)
from app.connectors.retry import ConnectorRetryError

logger = structlog.get_logger()

HTTP_TIMEOUT = 30  # seconds


class HTTPConnector(BaseConnector):
    """Base class for HTTP-based connectors with shared request logic."""

    async def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> tuple[int, dict[str, Any] | None]:
        """Make an HTTP request and return (status_code, response_json)."""
        url = f"{self.base_url}{path}"
        headers = self._build_headers()

        try:
            async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                response = await client.request(
                    method, url, json=payload, params=params, headers=headers
                )
                data = response.json() if response.content else None
                return response.status_code, data
        except httpx.TimeoutException:
            raise ConnectorRetryError(f"Timeout connecting to {self.name}")
        except httpx.ConnectError:
            raise ConnectorRetryError(f"Cannot connect to {self.name}")

    async def health_check(self) -> ConnectorStatus:
        """Check health via GET /health."""
        try:
            status_code, _ = await self._request("GET", "/health")
            return ConnectorStatus.HEALTHY if status_code == 200 else ConnectorStatus.DEGRADED
        except Exception:
            return ConnectorStatus.DOWN

    def _make_diff(
        self, before: dict[str, Any], after: dict[str, Any]
    ) -> DiffResult:
        """Generate a structured diff between before and after states."""
        changes: list[DiffChange] = []
        all_keys = set(before.keys()) | set(after.keys())

        for key in sorted(all_keys):
            old = before.get(key)
            new = after.get(key)
            if key not in before:
                changes.append(DiffChange(field=key, new_value=new, change_type="add"))
            elif key not in after:
                changes.append(DiffChange(field=key, old_value=old, change_type="remove"))
            elif old != new:
                changes.append(DiffChange(field=key, old_value=old, new_value=new, change_type="modify"))

        diff = DiffResult(before=before, after=after, changes=changes)
        diff.compute_hash()
        return diff
