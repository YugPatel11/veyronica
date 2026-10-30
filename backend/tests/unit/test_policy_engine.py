"""Unit tests for Policy & Approval Engine.

EPIC-08-T11: Unit tests for policy engine:
- Risk classification matrix
- Approval routing decisions
- Policy rule evaluator
- Approval request creation with diff binding
- Critical invariant guard (cannot lower critical below dual_approval)
- Timeout & decision handling
"""

from __future__ import annotations

import pytest

from app.policy import (
    CRITICAL_OPERATIONS,
    ApprovalEngine,
    PolicyRule,
    RiskLevel,
    classify_risk,
    compute_diff_hash,
    determine_approval_type,
    evaluate_policy,
)


class TestRiskClassification:
    def test_critical_operation_always_critical(self) -> None:
        for op in CRITICAL_OPERATIONS:
            risk = classify_risk("campus-erp", op, autonomy="autonomous")
            assert risk == RiskLevel.CRITICAL

    def test_erp_default_high_risk(self) -> None:
        risk = classify_risk("campus-erp", "get_students", autonomy="supervised")
        assert risk == RiskLevel.HIGH

    def test_email_default_low_risk(self) -> None:
        risk = classify_risk("email-smtp", "send_email", autonomy="supervised")
        assert risk == RiskLevel.LOW

    def test_autonomous_mode_elevates_non_critical_risk(self) -> None:
        risk_sup = classify_risk("lms", "get_submissions", autonomy="supervised")
        risk_auto = classify_risk("lms", "get_submissions", autonomy="autonomous")
        assert risk_sup == RiskLevel.MEDIUM
        assert risk_auto == RiskLevel.HIGH


class TestApprovalRouting:
    def test_critical_risk_requires_dual_approval(self) -> None:
        # Critical actions require dual_approval regardless of autonomy
        assert determine_approval_type(RiskLevel.CRITICAL, "autonomous") == "dual_approval"
        assert determine_approval_type(RiskLevel.CRITICAL, "supervised") == "dual_approval"

    def test_high_risk_requires_approval(self) -> None:
        assert determine_approval_type(RiskLevel.MEDIUM, "supervised") == "approval"
        assert determine_approval_type(RiskLevel.HIGH, "autonomous") == "approval"
        assert determine_approval_type(RiskLevel.HIGH, "supervised") == "dual_approval"

    def test_low_risk_auto_approves(self) -> None:
        assert determine_approval_type(RiskLevel.LOW, "supervised") == "auto"


class TestPolicyEvaluation:
    def test_evaluates_condition_correctly(self) -> None:
        rule = PolicyRule(
            name="marks_deviation_check",
            condition="deviation <= 20",
            action="reject",
            message="Marks deviation exceeds threshold",
        )
        res = evaluate_policy([rule], {"deviation": 25})
        assert res.passed is False
        assert res.action == "reject"
        assert len(res.violations) == 1

    def test_handles_no_match(self) -> None:
        rule = PolicyRule(
            name="marks_deviation_check",
            condition="deviation <= 20",
            action="reject",
            message="Marks deviation exceeds threshold",
        )
        res = evaluate_policy([rule], {"deviation": 10})
        assert res.passed is True
        assert res.action == "approve"
        assert len(res.violations) == 0


class TestApprovalEngineRequests:
    def test_creates_request_with_diff_binding(self) -> None:
        engine = ApprovalEngine()
        diff_before = {"score": 50}
        diff_after = {"score": 85}
        expected_hash = compute_diff_hash(diff_before, diff_after)

        req = engine.create_request(
            run_id="run_101",
            task_id="publish_task",
            title="Publish CS301 marks",
            risk_level="high",
            approval_type="approval",
            diff_before=diff_before,
            diff_after=diff_after,
        )

        assert req.status == "pending"
        assert req.diff_hash == expected_hash

    def test_decide_approval_single(self) -> None:
        engine = ApprovalEngine()
        req = engine.create_request(
            run_id="run_102",
            task_id="task_1",
            title="Approve marks",
            approval_type="approval",
        )
        decided = engine.decide(req.id, approver_id="usr_001", decision="approved")
        assert decided.status == "approved"
        assert len(decided.decisions) == 1

    def test_dual_approval_flow_requires_two_different_approvers(self) -> None:
        engine = ApprovalEngine()
        req = engine.create_request(
            run_id="run_103",
            task_id="critical_publish",
            title="Publish Critical Marks",
            approval_type="dual_approval",
        )

        # First approver
        first_step = engine.decide(req.id, approver_id="usr_001", decision="approved")
        assert first_step.status == "pending"  # Still pending second approval

        # Same approver cannot approve twice
        with pytest.raises(ValueError, match="cannot approve twice"):
            engine.decide(req.id, approver_id="usr_001", decision="approved")

        # Second different approver
        final_step = engine.decide(req.id, approver_id="usr_002", decision="approved")
        assert final_step.status == "approved"
        assert len(final_step.decisions) == 2
