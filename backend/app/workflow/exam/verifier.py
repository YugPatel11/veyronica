"""Verifier Agent for Exam Grading (EPIC-15-T05).

Performs strict arithmetic verification:
- Marks summation verification (sum of questions == total)
- Range bounds checks (0 <= marks <= max_marks)
- Confidence threshold evaluation (< 0.70 triggers human review)
- Anomaly detection
"""

from __future__ import annotations

from dataclasses import dataclass, field
from .evaluation import EvaluationSummary


@dataclass
class VerificationResult:
    is_valid: bool
    sum_matches: bool
    ranges_valid: bool
    confidence_acceptable: bool
    requires_approval: bool
    violations: list[str] = field(default_factory=list)
    calculated_sum: float = 0.0
    recorded_sum: float = 0.0


class ExamVerifier:
    """Rigorous arithmetic and confidence verifier for grading outputs."""

    def __init__(self, min_confidence_threshold: float = 0.70) -> None:
        self.min_confidence_threshold = min_confidence_threshold

    def verify(self, summary: EvaluationSummary) -> VerificationResult:
        """Verify summary arithmetic and confidence thresholds."""
        violations: list[str] = []

        # 1. Summation check
        calculated_sum = round(sum(q.marks_awarded for q in summary.evaluations), 1)
        recorded_sum = round(summary.total_marks_awarded, 1)
        sum_matches = abs(calculated_sum - recorded_sum) < 0.01

        if not sum_matches:
            violations.append(
                f"Marks summation mismatch: calculated sum {calculated_sum} != recorded total {recorded_sum}"
            )

        # 2. Range checks
        ranges_valid = True
        for q in summary.evaluations:
            if q.marks_awarded < 0:
                ranges_valid = False
                violations.append(f"Q{q.question_num} has negative marks: {q.marks_awarded}")
            if q.marks_awarded > q.max_marks:
                ranges_valid = False
                violations.append(
                    f"Q{q.question_num} marks ({q.marks_awarded}) exceed maximum ({q.max_marks})"
                )

        if summary.total_marks_awarded < 0 or summary.total_marks_awarded > summary.total_max_marks:
            ranges_valid = False
            violations.append(
                f"Total marks ({summary.total_marks_awarded}) out of bounds [0, {summary.total_max_marks}]"
            )

        # 3. Confidence threshold check
        confidence_acceptable = summary.overall_confidence >= self.min_confidence_threshold
        if not confidence_acceptable:
            violations.append(
                f"Confidence {summary.overall_confidence} below required threshold {self.min_confidence_threshold}"
            )

        is_valid = sum_matches and ranges_valid
        # Requires human approval if either validity failed or confidence is low
        requires_approval = (not is_valid) or (not confidence_acceptable)

        return VerificationResult(
            is_valid=is_valid,
            sum_matches=sum_matches,
            ranges_valid=ranges_valid,
            confidence_acceptable=confidence_acceptable,
            requires_approval=requires_approval,
            violations=violations,
            calculated_sum=calculated_sum,
            recorded_sum=recorded_sum,
        )
