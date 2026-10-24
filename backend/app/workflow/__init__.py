"""Workflow Engine — YAML parser and execution.

EPIC-07-T01: YAML workflow definition parser with Pydantic validation.
EPIC-07-T03: RunState TypedDict.
EPIC-07-T09: Autonomy dial.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, TypedDict

import yaml
from pydantic import BaseModel, Field, field_validator


# ── Autonomy Levels ──────────────────────────────────────────────────────────

class AutonomyLevel(StrEnum):
    """EPIC-07-T09: Three autonomy levels."""
    ASSIST = "assist"        # Agent suggests, human executes
    SUPERVISED = "supervised"  # Agent executes, human approves critical
    AUTONOMOUS = "autonomous"  # Agent executes, no approval needed


# ── RunState ─────────────────────────────────────────────────────────────────

class RunState(TypedDict, total=False):
    """EPIC-07-T03: Complete workflow run state."""
    run_id: str
    definition_id: str
    workflow_name: str
    status: str  # pending, running, waiting_approval, completed, failed, cancelled
    autonomy: str
    current_step: str
    steps_completed: list[str]
    steps_remaining: list[str]
    trigger_type: str
    trigger_payload: dict[str, Any]
    initiated_by: str
    started_at: str
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    errors: list[dict[str, Any]]
    total_tokens: int
    total_cost_usd: float
    approval_pending: dict[str, Any] | None
    checkpoint_id: str


# ── Workflow YAML Schema ─────────────────────────────────────────────────────

class StepDefinition(BaseModel):
    """A single step in a workflow."""
    name: str
    type: str = "agent"  # agent, approval, branch, parallel, connector
    agent: str | None = None
    description: str = ""
    tools: list[str] = Field(default_factory=list)
    connector: str | None = None
    operation: str | None = None
    model_tier: str = "standard"
    timeout_seconds: int = 300
    retry_max: int = 2
    # Branch conditions
    when: str | None = None  # Python expression for conditionals
    branches: list[StepDefinition] | None = None
    # Parallel steps
    parallel_steps: list[StepDefinition] | None = None
    # Approval settings
    approval_type: str = "approval"  # approval, dual_approval, notify
    risk_level: str = "medium"

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        valid = {"agent", "approval", "branch", "parallel", "connector"}
        if v not in valid:
            raise ValueError(f"Invalid step type: {v}. Must be one of {valid}")
        return v


class WorkflowSchema(BaseModel):
    """EPIC-07-T01: Validated workflow definition."""
    name: str
    slug: str
    version: int = 1
    description: str = ""
    trigger: str = "manual"  # manual, webhook, scheduled, copilot
    autonomy_default: str = "supervised"
    steps: list[StepDefinition]
    on_failure: str = "escalate"  # escalate, retry, stop

    @field_validator("trigger")
    @classmethod
    def validate_trigger(cls, v: str) -> str:
        valid = {"manual", "webhook", "scheduled", "copilot"}
        if v not in valid:
            raise ValueError(f"Invalid trigger: {v}")
        return v


def parse_workflow_yaml(yaml_content: str) -> WorkflowSchema:
    """Parse and validate a YAML workflow definition.

    EPIC-07-T01: YAML parser with Pydantic validation.
    """
    data = yaml.safe_load(yaml_content)
    if not isinstance(data, dict):
        raise ValueError("Workflow YAML must be a mapping")
    return WorkflowSchema(**data)


# ── Workflow Definitions ─────────────────────────────────────────────────────

EXAM_MARKS_WORKFLOW = """
name: "Exam Marks Processing"
slug: "exam-marks-processing"
version: 1
description: "End-to-end exam marks ingestion, evaluation, verification, and publication"
trigger: manual
autonomy_default: supervised
on_failure: escalate
steps:
  - name: "Ingest Answer Sheets"
    type: agent
    agent: ingestion
    description: "Upload and OCR/extract answers from scanned sheets"
    model_tier: standard
    timeout_seconds: 600

  - name: "Evaluate Answers"
    type: agent
    agent: evaluation
    description: "Mark answers against rubrics with confidence scoring"
    model_tier: premium
    timeout_seconds: 900

  - name: "Verify Marks"
    type: agent
    agent: verifier
    description: "Cross-check marks totals, ranges, and confidence thresholds"
    model_tier: economy
    timeout_seconds: 120

  - name: "Approve Publication"
    type: approval
    approval_type: approval
    risk_level: high
    description: "Faculty approval before marks are published to ERP"

  - name: "Publish to ERP"
    type: connector
    connector: campus-erp
    operation: publish_marks
    description: "Push verified marks to the Campus ERP system"

  - name: "Notify Stakeholders"
    type: parallel
    parallel_steps:
      - name: "Email Faculty"
        type: agent
        agent: communication
        model_tier: economy
      - name: "Update CRM"
        type: connector
        connector: student-crm
        operation: create_note
"""

LEAVE_APPLICATION_WORKFLOW = """
name: "Leave Application Processing"
slug: "leave-application"
version: 1
description: "Student leave application review and processing"
trigger: webhook
autonomy_default: supervised
on_failure: escalate
steps:
  - name: "Validate Application"
    type: agent
    agent: verifier
    description: "Check leave dates, documentation, and policy compliance"
    model_tier: economy

  - name: "Assess Impact"
    type: agent
    agent: analysis
    description: "Check attendance record and academic impact"
    model_tier: standard

  - name: "Route for Approval"
    type: approval
    approval_type: approval
    risk_level: low

  - name: "Update ERP"
    type: connector
    connector: campus-erp
    operation: update_student

  - name: "Send Confirmation"
    type: agent
    agent: communication
    model_tier: economy
"""

# EPIC-07-T14: Pre-built workflow definitions
BUILTIN_WORKFLOWS = {
    "exam-marks-processing": EXAM_MARKS_WORKFLOW,
    "leave-application": LEAVE_APPLICATION_WORKFLOW,
}
