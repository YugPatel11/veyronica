"""Policy & Approval Engine.

EPIC-08-T01: Policy rule evaluator.
EPIC-08-T02: Risk classification.
EPIC-08-T03: Approval routing.
EPIC-08-T04: Approval request creation with diff binding.
EPIC-08-T05: Timeout and escalation.
EPIC-08-T06: Rejection handling.
EPIC-08-T07: Dual-approval flow.
EPIC-08-T08: Critical actions always require dual_approval.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger()


# ── Risk Classification ──────────────────────────────────────────────────────

class RiskLevel:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Connector risk × context matrix
CONNECTOR_RISK: dict[str, str] = {
    "campus-erp": "high",
    "lms": "medium",
    "student-crm": "medium",
    "email-smtp": "low",
    "object-storage": "low",
}

CRITICAL_OPERATIONS = {
    "publish_marks", "delete_student", "delete_marks",
    "update_grades", "bulk_update", "drop_course",
}


def classify_risk(
    connector_slug: str,
    operation: str,
    autonomy: str = "supervised",
) -> str:
    """EPIC-08-T02: Classify risk level."""
    if operation in CRITICAL_OPERATIONS:
        return RiskLevel.CRITICAL

    base_risk = CONNECTOR_RISK.get(connector_slug, RiskLevel.MEDIUM)

    if autonomy == "autonomous":
        # Elevate risk in autonomous mode
        if base_risk == RiskLevel.LOW:
            return RiskLevel.MEDIUM
        if base_risk == RiskLevel.MEDIUM:
            return RiskLevel.HIGH
        return RiskLevel.CRITICAL

    return base_risk


# ── Approval Routing ─────────────────────────────────────────────────────────

def determine_approval_type(risk_level: str, autonomy: str = "supervised") -> str:
    """EPIC-08-T03 / T08: Determine approval routing.

    Returns: auto, notify, approval, dual_approval
    """
    if risk_level == RiskLevel.CRITICAL:
        return "dual_approval"  # T08: Always dual for critical

    if autonomy == "autonomous":
        if risk_level == RiskLevel.LOW:
            return "auto"
        if risk_level == RiskLevel.MEDIUM:
            return "notify"
        return "approval"

    if autonomy == "supervised":
        if risk_level == RiskLevel.LOW:
            return "auto"
        if risk_level == RiskLevel.MEDIUM:
            return "approval"
        return "dual_approval"

    # assist mode — everything needs approval
    return "approval"


# ── Policy Evaluator ─────────────────────────────────────────────────────────

class PolicyRule(BaseModel):
    """A single policy rule."""
    name: str
    condition: str  # Python expression
    action: str  # approve, reject, escalate, require_approval
    message: str = ""


class PolicyResult(BaseModel):
    """Result of policy evaluation."""
    passed: bool = True
    action: str = "approve"
    violations: list[str] = Field(default_factory=list)
    rules_evaluated: int = 0


def evaluate_policy(
    rules: list[PolicyRule],
    context: dict[str, Any],
) -> PolicyResult:
    """EPIC-08-T01: Evaluate policy rules against context.

    Uses restricted eval for safety.
    """
    result = PolicyResult(rules_evaluated=len(rules))
    safe_builtins = {"abs": abs, "len": len, "max": max, "min": min, "sum": sum, "round": round, "True": True, "False": False}

    for rule in rules:
        try:
            passed = eval(rule.condition, {"__builtins__": safe_builtins}, context)  # noqa: S307
            if not passed:
                result.violations.append(f"{rule.name}: {rule.message}")
                if rule.action in ("reject", "escalate"):
                    result.passed = False
                    result.action = rule.action
        except Exception as e:
            logger.warning("policy_eval_error", rule=rule.name, error=str(e))

    return result


def compute_diff_hash(before: dict[str, Any], after: dict[str, Any]) -> str:
    """EPIC-08-T04: Compute deterministic SHA-256 hash of diff before/after."""
    import hashlib
    import json
    data = {"before": before, "after": after}
    canon = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(canon.encode()).hexdigest()


# ── Approval Request ─────────────────────────────────────────────────────────

class ApprovalRequestData(BaseModel):
    """EPIC-08-T04: Approval request with diff binding."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    run_id: str
    task_id: str
    approval_type: str  # approval, dual_approval, notify
    risk_level: str = "medium"
    title: str
    description: str = ""
    diff_hash: str | None = None
    diff_before: dict[str, Any] = Field(default_factory=dict)
    diff_after: dict[str, Any] = Field(default_factory=dict)
    status: str = "pending"
    timeout_minutes: int = 60
    expires_at: datetime | None = None
    required_approvals: int = 1
    decisions: list[ApprovalDecisionData] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def model_post_init(self, __context: Any) -> None:
        if not self.expires_at:
            self.expires_at = self.created_at + timedelta(minutes=self.timeout_minutes)
        if self.approval_type == "dual_approval":
            self.required_approvals = 2


class ApprovalDecisionData(BaseModel):
    """EPIC-08-T06: Approval decision with required reason for rejection."""
    approver_id: str
    decision: str  # approved, rejected
    reason: str = ""  # Required for rejection
    decided_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ApprovalEngine:
    """Manages approval lifecycle."""

    def __init__(self) -> None:
        self._requests: dict[str, ApprovalRequestData] = {}

    def create_request(self, **kwargs: Any) -> ApprovalRequestData:
        """EPIC-08-T04: Create an approval request."""
        if not kwargs.get("diff_hash") and (kwargs.get("diff_before") or kwargs.get("diff_after")):
            kwargs["diff_hash"] = compute_diff_hash(kwargs.get("diff_before", {}), kwargs.get("diff_after", {}))
        req = ApprovalRequestData(**kwargs)
        self._requests[req.id] = req
        logger.info("approval_request_created", id=req.id, type=req.approval_type, risk=req.risk_level)
        return req

    def decide(
        self, request_id: str, approver_id: str, decision: str, reason: str = ""
    ) -> ApprovalRequestData:
        """EPIC-08-T06/T07: Process an approval decision."""
        req = self._requests.get(request_id)
        if not req:
            raise ValueError(f"Approval request not found: {request_id}")

        if req.status != "pending":
            raise ValueError(f"Request is already {req.status}")

        # T06: Rejection requires reason
        if decision == "rejected" and not reason:
            raise ValueError("Rejection reason is required")

        # Check timeout (T05)
        if req.expires_at and datetime.now(UTC) > req.expires_at:
            req.status = "expired"
            raise ValueError("Approval request has expired")

        # T07: Check for duplicate approver in dual-approval
        if req.approval_type == "dual_approval":
            existing = [d.approver_id for d in req.decisions]
            if approver_id in existing:
                raise ValueError("Same approver cannot approve twice in dual-approval")

        dec = ApprovalDecisionData(approver_id=approver_id, decision=decision, reason=reason)
        req.decisions.append(dec)

        if decision == "rejected":
            req.status = "rejected"
        elif len([d for d in req.decisions if d.decision == "approved"]) >= req.required_approvals:
            req.status = "approved"

        logger.info("approval_decision", id=request_id, decision=decision, status=req.status)
        return req

    def get_pending(self) -> list[ApprovalRequestData]:
        return [r for r in self._requests.values() if r.status == "pending"]

    def check_expired(self) -> list[ApprovalRequestData]:
        """EPIC-08-T05: Check and mark expired requests."""
        expired = []
        now = datetime.now(UTC)
        for req in self._requests.values():
            if req.status == "pending" and req.expires_at and now > req.expires_at:
                req.status = "expired"
                expired.append(req)
                logger.warning("approval_expired", id=req.id)
        return expired


# Singleton
approval_engine = ApprovalEngine()

# ── Default Policy Rules ─────────────────────────────────────────────────────

DEFAULT_MARKS_POLICY = [
    PolicyRule(name="marks_range", condition="0 <= marks <= max_marks", action="reject", message="Marks out of valid range"),
    PolicyRule(name="confidence_threshold", condition="confidence >= 0.6", action="require_approval", message="Low confidence score"),
    PolicyRule(name="marks_change_limit", condition="abs(new_marks - old_marks) <= max_marks * 0.5", action="escalate", message="Marks change exceeds 50%"),
]

DEFAULT_DELETE_POLICY = [
    PolicyRule(name="no_bulk_delete", condition="count <= 10", action="reject", message="Cannot delete more than 10 records at once"),
    PolicyRule(name="require_reason", condition="len(reason) >= 10", action="reject", message="Delete reason must be at least 10 characters"),
]
