"""Workflow Engine API endpoints.

EPIC-07: Workflow engine, start runs, resume approvals, get checkpoints.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.workflow import (
    BUILTIN_WORKFLOWS,
    WorkflowSchema,
    parse_workflow_yaml,
)
from app.workflow.executor import executor

router = APIRouter(prefix="/workflows", tags=["Workflows"])


# ── Request/Response Models ──────────────────────────────────────────────────

class StartRunRequest(BaseModel):
    workflow_slug: str
    trigger_type: str = "manual"
    trigger_payload: dict[str, Any] = Field(default_factory=dict)
    initiated_by: str = ""
    autonomy: str = "supervised"
    input_data: dict[str, Any] = Field(default_factory=dict)


class ResumeApprovalRequest(BaseModel):
    approved: bool
    reason: str = ""


class WorkflowDefinitionResponse(BaseModel):
    name: str
    slug: str
    version: int
    description: str
    trigger: str
    autonomy_default: str
    steps_count: int
    on_failure: str


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/definitions", response_model=list[WorkflowDefinitionResponse])
async def list_workflow_definitions() -> list[WorkflowDefinitionResponse]:
    """List all built-in workflow definitions."""
    results = []
    for slug, yaml_content in BUILTIN_WORKFLOWS.items():
        schema = parse_workflow_yaml(yaml_content)
        results.append(WorkflowDefinitionResponse(
            name=schema.name,
            slug=schema.slug,
            version=schema.version,
            description=schema.description,
            trigger=schema.trigger,
            autonomy_default=schema.autonomy_default,
            steps_count=len(schema.steps),
            on_failure=schema.on_failure,
        ))
    return results


@router.get("/definitions/{slug}")
async def get_workflow_definition(slug: str) -> dict[str, Any]:
    """Get a specific workflow definition with full step details."""
    yaml_content = BUILTIN_WORKFLOWS.get(slug)
    if not yaml_content:
        raise HTTPException(status_code=404, detail=f"Workflow '{slug}' not found")
    schema = parse_workflow_yaml(yaml_content)
    return schema.model_dump()


@router.post("/runs")
async def start_workflow_run(body: StartRunRequest) -> dict[str, Any]:
    """Start a new workflow run."""
    yaml_content = BUILTIN_WORKFLOWS.get(body.workflow_slug)
    if not yaml_content:
        raise HTTPException(
            status_code=404,
            detail=f"Workflow '{body.workflow_slug}' not found",
        )

    schema = parse_workflow_yaml(yaml_content)
    state = await executor.start_run(
        schema,
        trigger_type=body.trigger_type,
        trigger_payload=body.trigger_payload,
        initiated_by=body.initiated_by,
        autonomy=body.autonomy,
        input_data=body.input_data,
    )
    return dict(state)


@router.post("/runs/{run_id}/approve")
async def resume_after_approval(
    run_id: str, body: ResumeApprovalRequest
) -> dict[str, Any]:
    """Resume a workflow run after an approval decision."""
    checkpoints = executor.get_checkpoints(run_id)
    if not checkpoints:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    # Use the latest checkpoint as current state
    state = checkpoints[-1]
    if state.get("status") != "waiting_approval":
        raise HTTPException(
            status_code=400,
            detail=f"Run is not waiting for approval (status: {state.get('status')})",
        )

    updated = await executor.resume_after_approval(state, body.approved, body.reason)
    return dict(updated)


@router.get("/runs/{run_id}/checkpoints")
async def get_run_checkpoints(run_id: str) -> list[dict[str, Any]]:
    """Get all checkpoints for a workflow run (Decision Replay).

    EPIC-07-T12: Checkpoint retrieval for Decision Replay.
    """
    checkpoints = executor.get_checkpoints(run_id)
    if not checkpoints:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    return [dict(c) for c in checkpoints]
