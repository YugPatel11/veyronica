"""Structured Decision Records for Exam Evaluation (EPIC-15-T04).

Produces immutable, auditable decision records documenting options considered,
selection rationale, confidence scores, and cryptographic fingerprinting.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from .evaluation import EvaluationSummary


@dataclass
class DecisionOption:
    option_id: str
    description: str
    proposed_action: str
    risk_level: str  # "low", "medium", "high"
    confidence: float


@dataclass
class StructuredDecisionRecord:
    decision_id: str
    run_id: str
    student_roll: str
    document_id: str
    timestamp: str
    options_considered: list[DecisionOption]
    selected_option_id: str
    rationale: str
    confidence: float
    requires_human_approval: bool
    evaluation_summary: dict[str, Any]
    decision_hash: str = ""

    def calculate_hash(self) -> str:
        """Compute SHA256 integrity hash of decision payload."""
        payload = {
            "decision_id": self.decision_id,
            "run_id": self.run_id,
            "student_roll": self.student_roll,
            "document_id": self.document_id,
            "selected_option_id": self.selected_option_id,
            "rationale": self.rationale,
            "confidence": self.confidence,
            "requires_human_approval": self.requires_human_approval,
            "evaluation_summary": self.evaluation_summary,
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


class DecisionRecordBuilder:
    """Builds structured decision records for evaluation results."""

    @staticmethod
    def create_decision(
        run_id: str,
        evaluation: EvaluationSummary,
        confidence_threshold: float = 0.70,
    ) -> StructuredDecisionRecord:
        """Construct an immutable decision record for an evaluated answer sheet."""
        ts = datetime.now(timezone.utc).isoformat()
        decision_id = f"dec_{run_id[:8]}_{evaluation.student_roll}"

        options = [
            DecisionOption(
                option_id="opt_auto_publish",
                description="Auto-approve marks and sync to ERP directly",
                proposed_action="PUBLISH_TO_ERP",
                risk_level="low",
                confidence=evaluation.overall_confidence,
            ),
            DecisionOption(
                option_id="opt_faculty_review",
                description="Route to faculty review queue due to low confidence or edge cases",
                proposed_action="REQUIRE_FACULTY_APPROVAL",
                risk_level="medium",
                confidence=evaluation.overall_confidence,
            ),
            DecisionOption(
                option_id="opt_re_evaluate",
                description="Rerun OCR and LLM evaluation with higher tier model",
                proposed_action="RERUN_EVALUATION",
                risk_level="low",
                confidence=0.5,
            ),
        ]

        # Determine option
        requires_approval = evaluation.overall_confidence < confidence_threshold
        if requires_approval:
            selected_option = "opt_faculty_review"
            rationale = (
                f"Overall confidence ({evaluation.overall_confidence}) is below threshold ({confidence_threshold}). "
                f"Routed for faculty verification."
            )
        else:
            selected_option = "opt_auto_publish"
            rationale = (
                f"Evaluation confidence ({evaluation.overall_confidence}) meets standards. "
                f"Marks auto-published with score {evaluation.total_marks_awarded}/{evaluation.total_max_marks}."
            )

        summary_dict = {
            "total_marks_awarded": evaluation.total_marks_awarded,
            "total_max_marks": evaluation.total_max_marks,
            "percentage": evaluation.percentage,
            "overall_confidence": evaluation.overall_confidence,
            "question_count": len(evaluation.evaluations),
        }

        record = StructuredDecisionRecord(
            decision_id=decision_id,
            run_id=run_id,
            student_roll=evaluation.student_roll,
            document_id=evaluation.document_id,
            timestamp=ts,
            options_considered=options,
            selected_option_id=selected_option,
            rationale=rationale,
            confidence=evaluation.overall_confidence,
            requires_human_approval=requires_approval,
            evaluation_summary=summary_dict,
        )
        record.decision_hash = record.calculate_hash()
        return record
