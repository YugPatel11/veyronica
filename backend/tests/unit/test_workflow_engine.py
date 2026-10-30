"""Unit tests for Workflow Engine & Master Agent execution.

EPIC-07-T15: Workflow engine unit tests:
- YAML parsing & step validation
- Autonomy dial behavior (assist, supervised, autonomous)
- Sequential step execution & state transitions
- Approval pause (interrupt) and resume
- Decision Replay checkpoints
"""

from __future__ import annotations

import pytest

from app.workflow import (
    BUILTIN_WORKFLOWS,
    AutonomyLevel,
    RunState,
    StepDefinition,
    WorkflowSchema,
    parse_workflow_yaml,
)
from app.workflow.executor import WorkflowExecutor


class TestWorkflowParsing:
    def test_parses_builtin_exam_workflow(self) -> None:
        raw_yaml = BUILTIN_WORKFLOWS["exam-marks-processing"]
        schema = parse_workflow_yaml(raw_yaml)
        assert schema.slug == "exam-marks-processing"
        assert len(schema.steps) == 6
        assert schema.autonomy_default == "supervised"

    def test_parses_builtin_leave_workflow(self) -> None:
        raw_yaml = BUILTIN_WORKFLOWS["leave-application"]
        schema = parse_workflow_yaml(raw_yaml)
        assert schema.slug == "leave-application"
        assert len(schema.steps) == 5

    def test_rejects_missing_name(self) -> None:
        invalid_yaml = "slug: test\nversion: 1\nsteps: []"
        with pytest.raises(Exception):
            parse_workflow_yaml(invalid_yaml)


class TestWorkflowExecution:
    @pytest.fixture
    def test_workflow(self) -> WorkflowSchema:
        yaml_content = """
name: "Test Workflow"
slug: "test-flow"
version: 1
description: "Test execution flow"
trigger: "manual"
autonomy_default: "supervised"
steps:
  - name: "step_ingest"
    type: "agent"
    agent: "ingestion"
    description: "Extract data"
    model_tier: "economy"
  - name: "step_approval"
    type: "approval"
    risk_level: "high"
    approval_type: "approval"
    description: "Approve extracted data"
  - name: "step_publish"
    type: "agent"
    agent: "evaluation"
    description: "Publish data"
    model_tier: "economy"
"""
        return parse_workflow_yaml(yaml_content)

    @pytest.mark.asyncio
    async def test_pauses_for_approval_in_supervised_mode(self, test_workflow: WorkflowSchema) -> None:
        executor = WorkflowExecutor()
        state = await executor.start_run(test_workflow, autonomy="supervised")
        assert state["status"] == "waiting_approval"
        assert state["current_step"] == "step_approval"
        assert state["steps_completed"] == ["step_ingest"]
        assert state["approval_pending"] is not None

    @pytest.mark.asyncio
    async def test_auto_approves_in_autonomous_mode(self, test_workflow: WorkflowSchema) -> None:
        executor = WorkflowExecutor()
        state = await executor.start_run(test_workflow, autonomy="autonomous")
        assert state["status"] == "completed"
        assert "step_approval" in state.get("steps_completed", [])
        assert "step_publish" in state.get("steps_completed", [])

    @pytest.mark.asyncio
    async def test_resumes_after_approval_decision(self, test_workflow: WorkflowSchema) -> None:
        executor = WorkflowExecutor()
        state = await executor.start_run(test_workflow, autonomy="supervised")
        assert state["status"] == "waiting_approval"

        # Resume with approved=True
        updated = await executor.resume_after_approval(state, approved=True, reason="Looks accurate")
        assert updated["status"] == "running"
        assert updated["approval_pending"] is None
        assert "step_approval" in updated.get("steps_completed", [])

    @pytest.mark.asyncio
    async def test_decision_replay_checkpoints(self, test_workflow: WorkflowSchema) -> None:
        executor = WorkflowExecutor()
        state = await executor.start_run(test_workflow, autonomy="supervised")
        run_id = state["run_id"]

        checkpoints = executor.get_checkpoints(run_id)
        assert len(checkpoints) >= 2
        # Initial run state and step checkpoints recorded
        assert checkpoints[0]["run_id"] == run_id
