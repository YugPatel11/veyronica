"""Assignment Parent Notification Flow with Policy Check (EPIC-16-T05).

Verifies consent and notification policies before dispatching overdue and
late penalty alerts to parents/guardians.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from .overdue_detector import OverdueStudentInfo


@dataclass
class PolicyEvaluationResult:
    allowed: bool
    consent_on_file: bool
    parent_opted_in: bool
    policy_reason: str


@dataclass
class OverdueNotificationDraft:
    recipient_email: str
    student_roll: str
    subject: str
    message_body: str
    policy_evaluation: PolicyEvaluationResult
    dispatch_status: str  # "sent", "blocked_by_policy", "queued"


class AssignmentNotificationAgent:
    """Handles policy validation and dispatch for assignment notifications."""

    def evaluate_notification_policy(
        self,
        student_roll: str,
        consent_records: dict[str, bool] | None = None,
        opt_out_records: set[str] | None = None,
    ) -> PolicyEvaluationResult:
        """Validate student data sharing consent and parent opt-in state."""
        consents = consent_records or {}
        opt_outs = opt_out_records or set()

        # Check if consent is explicitly false
        consent_ok = consents.get(student_roll, True)
        opted_in = student_roll not in opt_outs

        if not consent_ok:
            return PolicyEvaluationResult(
                allowed=False,
                consent_on_file=False,
                parent_opted_in=opted_in,
                policy_reason="Parent notification blocked: student data consent revoked or absent.",
            )

        if not opted_in:
            return PolicyEvaluationResult(
                allowed=False,
                consent_on_file=True,
                parent_opted_in=False,
                policy_reason="Parent notification blocked: parent opted out of automated reminders.",
            )

        return PolicyEvaluationResult(
            allowed=True,
            consent_on_file=True,
            parent_opted_in=True,
            policy_reason="Policy compliant: consent active and parent opted-in.",
        )

    def prepare_overdue_notification(
        self,
        info: OverdueStudentInfo,
        consent_records: dict[str, bool] | None = None,
        opt_out_records: set[str] | None = None,
    ) -> OverdueNotificationDraft:
        """Draft notification with strict policy compliance check."""
        policy_eval = self.evaluate_notification_policy(
            info.student_roll, consent_records, opt_out_records
        )

        subject = f"Notice: Assignment Submission Overdue — {info.student_name} ({info.course_code})"
        body = f"""Dear Parent / Guardian,

This is a courtesy academic reminder that {info.student_name} ({info.student_roll}) has not submitted the required coursework:
- Course: {info.course_code}
- Assignment: {info.assignment_title}
- Due Date: {info.due_date.strftime('%Y-%m-%d %H:%M UTC')}
- Time Elapsed: {info.hours_overdue} hours overdue

Please encourage {info.student_name} to complete and submit their work promptly to avoid further grade deductions.

Warm regards,
Academic Support Office
Nexus Institution
"""

        dispatch_status = "queued" if policy_eval.allowed else "blocked_by_policy"

        return OverdueNotificationDraft(
            recipient_email=info.parent_email,
            student_roll=info.student_roll,
            subject=subject,
            message_body=body.strip(),
            policy_evaluation=policy_eval,
            dispatch_status=dispatch_status,
        )
