"""Approval Engine API endpoints.

EPIC-08: Policy & Approval Engine.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.policy import (
    ApprovalRequestData,
    approval_engine,
    classify_risk,
    determine_approval_type,
    evaluate_policy,
    PolicyRule,
    PolicyResult,
    DEFAULT_MARKS_POLICY,
    DEFAULT_DELETE_POLICY,
)

router = APIRouter(prefix="/approvals", tags=["Approvals"])


# ── Request/Response Models ──────────────────────────────────────────────────

class CreateApprovalRequest(BaseModel):
    run_id: str
    task_id: str
    title: str
    description: str = ""
    risk_level: str = "medium"
    approval_type: str = "approval"
    diff_before: dict[str, Any] = Field(default_factory=dict)
    diff_after: dict[str, Any] = Field(default_factory=dict)
    diff_hash: str | None = None
    timeout_minutes: int = 60


class DecisionRequest(BaseModel):
    approver_id: str
    decision: str  # approved, rejected
    reason: str = ""


class RiskClassifyRequest(BaseModel):
    connector_slug: str
    operation: str
    autonomy: str = "supervised"


class PolicyEvalRequest(BaseModel):
    policy_name: str = "marks"  # marks, delete
    context: dict[str, Any] = Field(default_factory=dict)


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/pending")
async def list_pending_approvals() -> list[dict[str, Any]]:
    """List all pending approval requests."""
    return [r.model_dump(mode="json") for r in approval_engine.get_pending()]


@router.post("/")
async def create_approval(body: CreateApprovalRequest) -> dict[str, Any]:
    """Create a new approval request."""
    req = approval_engine.create_request(**body.model_dump())
    return req.model_dump(mode="json")


@router.post("/{request_id}/decide")
async def decide_approval(request_id: str, body: DecisionRequest) -> dict[str, Any]:
    """Submit an approval or rejection decision."""
    try:
        req = approval_engine.decide(
            request_id=request_id,
            approver_id=body.approver_id,
            decision=body.decision,
            reason=body.reason,
        )
        return req.model_dump(mode="json")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/expired")
async def check_expired() -> list[dict[str, Any]]:
    """Check and return expired approval requests."""
    expired = approval_engine.check_expired()
    return [r.model_dump(mode="json") for r in expired]


@router.post("/classify-risk")
async def classify_risk_endpoint(body: RiskClassifyRequest) -> dict[str, str]:
    """Classify the risk level of a connector operation.

    EPIC-08-T02: Risk classification.
    """
    risk = classify_risk(body.connector_slug, body.operation, body.autonomy)
    approval_type = determine_approval_type(risk, body.autonomy)
    return {"risk_level": risk, "approval_type": approval_type}


@router.post("/evaluate-policy")
async def evaluate_policy_endpoint(body: PolicyEvalRequest) -> PolicyResult:
    """Evaluate policy rules against context.

    EPIC-08-T01: Policy rule evaluator.
    """
    policy_map = {
        "marks": DEFAULT_MARKS_POLICY,
        "delete": DEFAULT_DELETE_POLICY,
    }
    rules = policy_map.get(body.policy_name, [])
    if not rules:
        raise HTTPException(status_code=404, detail=f"Policy '{body.policy_name}' not found")
    return evaluate_policy(rules, body.context)
