"""Assignment Submission Classifier Agent (EPIC-16-T01).

Classifies assignment submissions based on deadlines, grace periods,
late penalty tiers, and hard submission cutoffs.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum


class SubmissionStatus(StrEnum):
    ON_TIME = "on_time"
    GRACE_PERIOD = "grace_period"
    LATE_PENALIZED = "late_penalized"
    REJECTED_PAST_CUTOFF = "rejected_past_cutoff"


@dataclass
class ClassificationResult:
    submission_id: str
    student_roll: str
    status: SubmissionStatus
    delay_seconds: float
    penalty_percentage: float
    is_acceptable: bool
    rationale: str


class SubmissionClassifierAgent:
    """Classifies assignment submissions against course deadline policies."""

    def __init__(
        self,
        grace_period_seconds: int = 900,  # 15 minutes grace period
        penalty_per_hour_percent: float = 5.0,  # 5% deduction per hour late
        hard_cutoff_hours: int = 48,  # Rejections after 48h
    ) -> None:
        self.grace_period_seconds = grace_period_seconds
        self.penalty_per_hour = penalty_per_hour_percent
        self.hard_cutoff_seconds = hard_cutoff_hours * 3600

    def classify(
        self,
        submission_id: str,
        student_roll: str,
        due_date: datetime,
        submitted_at: datetime,
    ) -> ClassificationResult:
        """Classify submission timing and compute any late deduction penalty."""
        # Ensure UTC timezone awareness
        if due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=timezone.utc)
        if submitted_at.tzinfo is None:
            submitted_at = submitted_at.replace(tzinfo=timezone.utc)

        delay_seconds = (submitted_at - due_date).total_seconds()

        if delay_seconds <= 0:
            return ClassificationResult(
                submission_id=submission_id,
                student_roll=student_roll,
                status=SubmissionStatus.ON_TIME,
                delay_seconds=0.0,
                penalty_percentage=0.0,
                is_acceptable=True,
                rationale="Submitted on or before the official due date.",
            )

        if delay_seconds <= self.grace_period_seconds:
            return ClassificationResult(
                submission_id=submission_id,
                student_roll=student_roll,
                status=SubmissionStatus.GRACE_PERIOD,
                delay_seconds=delay_seconds,
                penalty_percentage=0.0,
                is_acceptable=True,
                rationale=f"Submitted within {self.grace_period_seconds // 60}-minute grace period. No penalty applied.",
            )

        if delay_seconds > self.hard_cutoff_seconds:
            return ClassificationResult(
                submission_id=submission_id,
                student_roll=student_roll,
                status=SubmissionStatus.REJECTED_PAST_CUTOFF,
                delay_seconds=delay_seconds,
                penalty_percentage=100.0,
                is_acceptable=False,
                rationale=f"Submitted {round(delay_seconds / 3600, 1)}h late, exceeding hard cutoff limit of {self.hard_cutoff_seconds // 3600}h.",
            )

        # Tiered late penalty
        hours_late = delay_seconds / 3600.0
        penalty = min(50.0, round(hours_late * self.penalty_per_hour, 1))

        return ClassificationResult(
            submission_id=submission_id,
            student_roll=student_roll,
            status=SubmissionStatus.LATE_PENALIZED,
            delay_seconds=delay_seconds,
            penalty_percentage=penalty,
            is_acceptable=True,
            rationale=f"Submitted {round(hours_late, 1)}h late. Applied {penalty}% late submission deduction.",
        )
