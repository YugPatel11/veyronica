import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
import pytest
from app.workflow.assignment import (
    SubmissionClassifierAgent,
    SubmissionStatus,
    AssignmentWebhookHandler,
    AssignmentERPSyncAgent,
    OverdueDetector,
    AssignmentNotificationAgent,
)


def test_submission_classifier_timing_tiers():
    classifier = SubmissionClassifierAgent(
        grace_period_seconds=900,
        penalty_per_hour_percent=5.0,
        hard_cutoff_hours=48,
    )
    due_date = datetime(2026, 11, 1, 12, 0, 0, tzinfo=timezone.utc)

    # 1. On time
    res_on_time = classifier.classify(
        "sub_1", "CS-101", due_date, due_date - timedelta(minutes=5)
    )
    assert res_on_time.status == SubmissionStatus.ON_TIME
    assert res_on_time.penalty_percentage == 0.0
    assert res_on_time.is_acceptable is True

    # 2. Grace period (10 mins late, within 15 min grace)
    res_grace = classifier.classify(
        "sub_2", "CS-102", due_date, due_date + timedelta(minutes=10)
    )
    assert res_grace.status == SubmissionStatus.GRACE_PERIOD
    assert res_grace.penalty_percentage == 0.0
    assert res_grace.is_acceptable is True

    # 3. Late penalized (4 hours late -> 20% penalty)
    res_late = classifier.classify(
        "sub_3", "CS-103", due_date, due_date + timedelta(hours=4)
    )
    assert res_late.status == SubmissionStatus.LATE_PENALIZED
    assert res_late.penalty_percentage == 20.0
    assert res_late.is_acceptable is True

    # 4. Past cutoff (50 hours late -> rejected)
    res_cutoff = classifier.classify(
        "sub_4", "CS-104", due_date, due_date + timedelta(hours=50)
    )
    assert res_cutoff.status == SubmissionStatus.REJECTED_PAST_CUTOFF
    assert res_cutoff.is_acceptable is False


def test_assignment_webhook_signature_and_idempotency():
    secret = "secret-test-key"
    handler = AssignmentWebhookHandler(secret_key=secret)

    payload_dict = {
        "event_id": "evt_asgn_999",
        "assignment_id": "asgn_algo_1",
        "student_roll": "CS2026-050",
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }
    raw_bytes = json.dumps(payload_dict).encode("utf-8")

    # Correct HMAC signature
    sig = hmac.new(secret.encode("utf-8"), raw_bytes, hashlib.sha256).hexdigest()

    # Success
    res = handler.process_webhook(raw_bytes, sig)
    assert res.is_valid is True
    assert res.status == "accepted"
    assert res.run_id is not None

    # Idempotent deduplication (same event processed again)
    res_dup = handler.process_webhook(raw_bytes, sig)
    assert res_dup.status == "duplicate_ignored"

    # Bad signature
    res_bad = handler.process_webhook(raw_bytes, "invalid_sig_abc123")
    assert res_bad.is_valid is False
    assert res_bad.status == "signature_failed"


def test_assignment_erp_sync():
    sync_agent = AssignmentERPSyncAgent()
    res = sync_agent.sync_marks(
        sync_id="sync_001",
        assignment_id="asgn_algo_1",
        student_roll="CS2026-010",
        raw_marks=90.0,
        penalty_percentage=10.0,  # 10% penalty -> 9 marks deducted
        max_marks=100.0,
    )
    assert res.status == "synced"
    assert res.penalty_deduction == 9.0
    assert res.final_marks == 81.0
    assert res.erp_reference_code is not None


def test_overdue_detector_scanning():
    detector = OverdueDetector()
    now = datetime(2026, 11, 2, 12, 0, 0, tzinfo=timezone.utc)
    due_date = datetime(2026, 11, 1, 12, 0, 0, tzinfo=timezone.utc)  # 24h ago

    assignments = [{"id": "asgn_1", "title": "Dynamic Programming", "course_code": "CS301", "due_date": due_date}]
    students = [
        {"roll": "CS-01", "name": "Aarav", "parent_email": "p1@example.com"},
        {"roll": "CS-02", "name": "Diya", "parent_email": "p2@example.com"},
    ]
    submissions = [{"assignment_id": "asgn_1", "student_roll": "CS-01"}]  # Only CS-01 submitted

    report = detector.scan_overdue_assignments(assignments, students, submissions, current_time=now)

    assert report.assignments_scanned == 1
    assert report.total_overdue_detected == 1
    assert report.overdue_students[0].student_roll == "CS-02"
    assert report.overdue_students[0].hours_overdue == 24.0


def test_parent_notification_with_policy_checks():
    agent = AssignmentNotificationAgent()
    now = datetime.now(timezone.utc)
    from app.workflow.assignment.overdue_detector import OverdueStudentInfo

    info = OverdueStudentInfo(
        student_roll="CS-02",
        student_name="Diya",
        parent_email="parent@example.com",
        assignment_id="asgn_1",
        assignment_title="Dynamic Programming",
        course_code="CS301",
        due_date=now - timedelta(hours=12),
        hours_overdue=12.0,
    )

    # 1. Allowed when consent active
    draft_ok = agent.prepare_overdue_notification(info, consent_records={"CS-02": True})
    assert draft_ok.policy_evaluation.allowed is True
    assert draft_ok.dispatch_status == "queued"
    assert "Overdue" in draft_ok.subject

    # 2. Blocked when consent revoked
    draft_blocked = agent.prepare_overdue_notification(info, consent_records={"CS-02": False})
    assert draft_blocked.policy_evaluation.allowed is False
    assert draft_blocked.dispatch_status == "blocked_by_policy"

    # 3. Blocked when parent opted out
    draft_optout = agent.prepare_overdue_notification(info, opt_out_records={"CS-02"})
    assert draft_optout.policy_evaluation.allowed is False
    assert draft_optout.dispatch_status == "blocked_by_policy"
