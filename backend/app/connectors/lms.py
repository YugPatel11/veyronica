"""LMS Connector Adapter. EPIC-05-T08."""
from __future__ import annotations
from typing import Any
from app.connectors import ConnectorResult
from app.connectors.http_connector import HTTPConnector

class LMSConnector(HTTPConnector):
    """Learning Management System connector."""
    OPERATIONS = {"get_courses", "get_course", "get_assignments", "submit_grade", "get_submissions", "create_assignment"}

    async def execute(self, operation: str, payload: dict[str, Any] | None = None, *, dry_run: bool = False, idempotency_key: str | None = None) -> ConnectorResult:
        payload = payload or {}
        if operation not in self.OPERATIONS:
            return ConnectorResult(success=False, error=f"Unknown LMS operation: {operation}")
        if operation == "get_courses":
            code, data = await self._request("GET", "/api/courses", params=payload)
        elif operation == "get_course":
            code, data = await self._request("GET", f"/api/courses/{payload.get('course_id')}")
        elif operation == "get_assignments":
            code, data = await self._request("GET", "/api/assignments", params=payload)
        elif operation == "get_submissions":
            code, data = await self._request("GET", "/api/submissions", params=payload)
        elif operation == "submit_grade":
            if dry_run:
                code, current = await self._request("GET", f"/api/submissions/{payload.get('submission_id')}")
                diff = self._make_diff(current or {}, payload)
                return ConnectorResult(success=True, data=payload, is_dry_run=True, diff=diff, idempotency_key=idempotency_key)
            code, data = await self._request("POST", "/api/grades", payload=payload)
        elif operation == "create_assignment":
            code, data = await self._request("POST", "/api/assignments", payload=payload)
        else:
            return ConnectorResult(success=False, error=f"Unhandled: {operation}")
        return ConnectorResult(success=code in (200, 201), data=data, status_code=code, idempotency_key=idempotency_key)
