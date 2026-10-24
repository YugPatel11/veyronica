"""ERP Connector Adapter.

EPIC-05-T07: Campus ERP connector (marks, students, subjects, faculty).
"""

from __future__ import annotations

from typing import Any

from app.connectors import ConnectorResult
from app.connectors.http_connector import HTTPConnector


class ERPConnector(HTTPConnector):
    """Campus ERP system connector.

    Operations: get_students, get_subjects, get_marks, publish_marks,
    update_student, get_faculty, get_divisions.
    """

    OPERATIONS = {
        "get_students", "get_student", "get_subjects", "get_marks",
        "publish_marks", "update_marks", "update_student",
        "get_faculty", "get_divisions", "get_attendance",
    }

    async def execute(
        self,
        operation: str,
        payload: dict[str, Any] | None = None,
        *,
        dry_run: bool = False,
        idempotency_key: str | None = None,
    ) -> ConnectorResult:
        payload = payload or {}

        if operation not in self.OPERATIONS:
            return ConnectorResult(success=False, error=f"Unknown ERP operation: {operation}")

        if operation == "get_students":
            code, data = await self._request("GET", "/api/students", params=payload)
            return ConnectorResult(success=code == 200, data=data, status_code=code)

        if operation == "get_student":
            sid = payload.get("student_id", "")
            code, data = await self._request("GET", f"/api/students/{sid}")
            return ConnectorResult(success=code == 200, data=data, status_code=code)

        if operation == "get_subjects":
            code, data = await self._request("GET", "/api/subjects", params=payload)
            return ConnectorResult(success=code == 200, data=data, status_code=code)

        if operation == "get_marks":
            code, data = await self._request("GET", "/api/marks", params=payload)
            return ConnectorResult(success=code == 200, data=data, status_code=code)

        if operation == "publish_marks":
            if dry_run:
                code, current = await self._request("GET", "/api/marks", params={"subject_id": payload.get("subject_id")})
                diff = self._make_diff(current or {}, payload)
                return ConnectorResult(success=True, data=payload, is_dry_run=True, diff=diff, idempotency_key=idempotency_key)
            code, data = await self._request("POST", "/api/marks/publish", payload=payload)
            return ConnectorResult(success=code in (200, 201), data=data, status_code=code, idempotency_key=idempotency_key)

        if operation == "update_marks":
            if dry_run:
                code, current = await self._request("GET", "/api/marks", params={"student_id": payload.get("student_id")})
                diff = self._make_diff(current or {}, payload)
                return ConnectorResult(success=True, data=payload, is_dry_run=True, diff=diff, idempotency_key=idempotency_key)
            code, data = await self._request("PUT", "/api/marks", payload=payload)
            return ConnectorResult(success=code == 200, data=data, status_code=code, idempotency_key=idempotency_key)

        if operation == "get_faculty":
            code, data = await self._request("GET", "/api/faculty", params=payload)
            return ConnectorResult(success=code == 200, data=data, status_code=code)

        if operation == "get_divisions":
            code, data = await self._request("GET", "/api/divisions", params=payload)
            return ConnectorResult(success=code == 200, data=data, status_code=code)

        if operation == "get_attendance":
            code, data = await self._request("GET", "/api/attendance", params=payload)
            return ConnectorResult(success=code == 200, data=data, status_code=code)

        if operation == "update_student":
            sid = payload.pop("student_id", "")
            if dry_run:
                code, current = await self._request("GET", f"/api/students/{sid}")
                diff = self._make_diff(current or {}, payload)
                return ConnectorResult(success=True, data=payload, is_dry_run=True, diff=diff)
            code, data = await self._request("PUT", f"/api/students/{sid}", payload=payload)
            return ConnectorResult(success=code == 200, data=data, status_code=code)

        return ConnectorResult(success=False, error=f"Unhandled operation: {operation}")
