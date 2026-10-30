"""HR System Connector Adapter.

EPIC-22-T02: HR connector stub (leave balance, apply leave, get employee).
"""

from __future__ import annotations

from typing import Any

from app.connectors import ConnectorResult, ConnectorStatus, DiffResult
from app.connectors.http_connector import HTTPConnector


class HRConnector(HTTPConnector):
    """Human Resources & Faculty Leave Connector.

    Operations: get_leave_balance, apply_leave, get_employee, cancel_leave.
    """

    OPERATIONS = {
        "get_leave_balance",
        "apply_leave",
        "get_employee",
        "cancel_leave",
    }

    def __init__(
        self,
        base_url: str = "http://localhost:8000/mock/hr",
        api_key: str = "mock-hr-key",
    ) -> None:
        super().__init__(
            connector_id="hr-system",
            name="HR & Staff Management",
            base_url=base_url,
            auth_config={"api_key": api_key},
        )
        # Mock in-memory storage for stub operations
        self._leave_balances: dict[str, dict[str, int]] = {
            "EMP-001": {"casual": 8, "medical": 12, "earned": 15},
            "EMP-002": {"casual": 4, "medical": 10, "earned": 20},
            "EMP-003": {"casual": 10, "medical": 14, "earned": 18},
        }
        self._applications: list[dict[str, Any]] = []

    async def health_check(self) -> ConnectorStatus:
        """Return healthy for HR connector stub."""
        return ConnectorStatus.HEALTHY

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
            return ConnectorResult(
                success=False,
                error=f"Unknown HR operation: {operation}",
                connector_id=self.connector_id,
                operation=operation,
            )

        if operation == "get_leave_balance":
            emp_id = payload.get("employee_id", "EMP-001")
            balance = self._leave_balances.get(emp_id, {"casual": 10, "medical": 10, "earned": 15})
            return ConnectorResult(
                success=True,
                data={"employee_id": emp_id, "balance": balance},
                connector_id=self.connector_id,
                operation=operation,
            )

        if operation == "get_employee":
            emp_id = payload.get("employee_id", "EMP-001")
            return ConnectorResult(
                success=True,
                data={
                    "employee_id": emp_id,
                    "name": payload.get("name", "Dr. Priya Sharma"),
                    "department": "Computer Science",
                    "designation": "Associate Professor",
                },
                connector_id=self.connector_id,
                operation=operation,
            )

        if operation == "apply_leave":
            emp_id = payload.get("employee_id", "EMP-001")
            leave_type = payload.get("leave_type", "casual")
            days = payload.get("days", 1)

            current_balance = self._leave_balances.get(emp_id, {"casual": 10, "medical": 10, "earned": 15})
            remaining = current_balance.get(leave_type, 0)

            if dry_run:
                diff = DiffResult(
                    before={leave_type: remaining},
                    after={leave_type: max(0, remaining - days)},
                )
                return ConnectorResult(
                    success=True,
                    is_dry_run=True,
                    diff=diff,
                    data={"preview": f"Deduct {days} days from {leave_type} leave"},
                    connector_id=self.connector_id,
                    operation=operation,
                )

            if remaining < days:
                return ConnectorResult(
                    success=False,
                    error=f"Insufficient leave balance: requested {days}, available {remaining}",
                    connector_id=self.connector_id,
                    operation=operation,
                )

            # Deduct balance
            current_balance[leave_type] = remaining - days
            record = {
                "application_id": f"LA-{len(self._applications) + 1:04d}",
                "employee_id": emp_id,
                "leave_type": leave_type,
                "days": days,
                "status": "approved",
            }
            self._applications.append(record)

            return ConnectorResult(
                success=True,
                data=record,
                connector_id=self.connector_id,
                operation=operation,
                idempotency_key=idempotency_key,
            )

        if operation == "cancel_leave":
            app_id = payload.get("application_id", "")
            return ConnectorResult(
                success=True,
                data={"application_id": app_id, "status": "cancelled"},
                connector_id=self.connector_id,
                operation=operation,
            )

        return ConnectorResult(
            success=False,
            error=f"Unhandled operation: {operation}",
            connector_id=self.connector_id,
            operation=operation,
        )
