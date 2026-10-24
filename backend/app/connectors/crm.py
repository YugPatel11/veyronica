"""CRM Connector Adapter. EPIC-05-T09."""
from __future__ import annotations
from typing import Any
from app.connectors import ConnectorResult
from app.connectors.http_connector import HTTPConnector

class CRMConnector(HTTPConnector):
    """Student CRM connector."""
    OPERATIONS = {"get_contacts", "get_contact", "update_contact", "create_note", "get_pipeline", "move_stage"}

    async def execute(self, operation: str, payload: dict[str, Any] | None = None, *, dry_run: bool = False, idempotency_key: str | None = None) -> ConnectorResult:
        payload = payload or {}
        if operation not in self.OPERATIONS:
            return ConnectorResult(success=False, error=f"Unknown CRM operation: {operation}")
        if operation == "get_contacts":
            code, data = await self._request("GET", "/api/contacts", params=payload)
        elif operation == "get_contact":
            code, data = await self._request("GET", f"/api/contacts/{payload.get('contact_id')}")
        elif operation == "update_contact":
            cid = payload.pop("contact_id", "")
            if dry_run:
                code, current = await self._request("GET", f"/api/contacts/{cid}")
                diff = self._make_diff(current or {}, payload)
                return ConnectorResult(success=True, data=payload, is_dry_run=True, diff=diff)
            code, data = await self._request("PUT", f"/api/contacts/{cid}", payload=payload)
        elif operation == "create_note":
            code, data = await self._request("POST", "/api/notes", payload=payload)
        elif operation == "get_pipeline":
            code, data = await self._request("GET", "/api/pipeline", params=payload)
        elif operation == "move_stage":
            code, data = await self._request("POST", "/api/pipeline/move", payload=payload)
        else:
            return ConnectorResult(success=False, error=f"Unhandled: {operation}")
        return ConnectorResult(success=code in (200, 201), data=data, status_code=code, idempotency_key=idempotency_key)
