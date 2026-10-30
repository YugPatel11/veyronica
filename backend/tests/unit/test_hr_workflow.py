"""Integration tests for HR Leave Template Extensibility.

EPIC-22: HR leave template workflow, HR connector stub, and same-engine execution proof.
"""

import pytest

from app.connectors.hr import HRConnector
from app.connectors.registry import registry
from app.workflow import BUILTIN_WORKFLOWS, parse_workflow_yaml
from app.workflow.executor import WorkflowExecutor


class TestHRConnector:
    """EPIC-22-T02: Tests for HR connector adapter."""

    @pytest.mark.asyncio
    async def test_get_leave_balance(self):
        connector = HRConnector()
        result = await connector.execute("get_leave_balance", {"employee_id": "EMP-001"})
        assert result.success is True
        assert result.data["employee_id"] == "EMP-001"
        assert "casual" in result.data["balance"]

    @pytest.mark.asyncio
    async def test_apply_leave_dry_run_diff(self):
        connector = HRConnector()
        result = await connector.execute(
            "apply_leave",
            {"employee_id": "EMP-001", "leave_type": "casual", "days": 2},
            dry_run=True,
        )
        assert result.success is True
        assert result.is_dry_run is True
        assert result.diff is not None
        assert result.diff.before["casual"] == 8
        assert result.diff.after["casual"] == 6

    @pytest.mark.asyncio
    async def test_apply_leave_execution(self):
        connector = HRConnector()
        result = await connector.execute(
            "apply_leave",
            {"employee_id": "EMP-002", "leave_type": "medical", "days": 3},
        )
        assert result.success is True
        assert result.data["status"] == "approved"
        assert result.data["employee_id"] == "EMP-002"

        # Check balance was deducted
        balance_res = await connector.execute("get_leave_balance", {"employee_id": "EMP-002"})
        assert balance_res.data["balance"]["medical"] == 7

    @pytest.mark.asyncio
    async def test_apply_leave_insufficient_balance(self):
        connector = HRConnector()
        result = await connector.execute(
            "apply_leave",
            {"employee_id": "EMP-002", "leave_type": "casual", "days": 99},
        )
        assert result.success is False
        assert "Insufficient leave balance" in (result.error or "")


class TestHRWorkflowExecution:
    """EPIC-22-T03: Integration test proving same-engine execution."""

    def test_parse_hr_workflow_yaml(self):
        yaml_content = BUILTIN_WORKFLOWS["leave-request"]
        schema = parse_workflow_yaml(yaml_content)
        assert schema.name == "Faculty & Staff Leave Request"
        assert schema.slug == "leave-request"
        assert len(schema.steps) == 5

    @pytest.mark.asyncio
    async def test_hr_workflow_same_engine_execution(self):
        # Register HR connector in the singleton registry
        hr_conn = HRConnector()
        registry.register(hr_conn)

        yaml_content = BUILTIN_WORKFLOWS["leave-request"]
        schema = parse_workflow_yaml(yaml_content)
        engine = WorkflowExecutor()

        # Execute under supervised mode: should execute Check Leave Balance and Coverage, then pause at HOD Approval
        state = await engine.start_run(
            schema,
            autonomy="supervised",
            input_data={"employee_id": "EMP-003", "leave_type": "casual", "days": 2},
        )

        assert state["status"] == "waiting_approval"
        assert state["current_step"] == "HOD Approval"
        assert "Check Leave Balance" in state["steps_completed"]

        # Resume after approval
        resumed = await engine.resume_after_approval(state, approved=True, reason="HOD approved")
        assert resumed["status"] == "running"
        assert resumed["approval_pending"] is None
        assert "HOD Approval" in resumed["steps_completed"]
