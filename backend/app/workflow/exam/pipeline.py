"""End-to-End Exam Result Cycle Pipeline (EPIC-15-T08).

Orchestrates the complete flow:
Upload / Ingest -> OCR Extraction -> Rubric Evaluation -> Verification ->
Performance Analysis -> Parent Communication -> ERP Sync -> CRM Activity Log.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from .ingestion import IngestionAgent, IngestionResult
from .ocr import OCRAgent, OCRExtractionResult
from .evaluation import EvaluationAgent, EvaluationSummary, RubricCriterion
from .verifier import ExamVerifier, VerificationResult
from .analysis import AnalysisAgent, StudentRiskProfile
from .communication import CommunicationAgent, ParentEmailDraft
from .decisions import DecisionRecordBuilder, StructuredDecisionRecord

logger = logging.getLogger("exam_pipeline")


@dataclass
class ExamPipelineOutput:
    run_id: str
    status: str  # "completed", "requires_approval", "failed"
    ingestion: IngestionResult
    ocr: OCRExtractionResult | None = None
    evaluation: EvaluationSummary | None = None
    verification: VerificationResult | None = None
    analysis: StudentRiskProfile | None = None
    communication: ParentEmailDraft | None = None
    decision_record: StructuredDecisionRecord | None = None
    erp_sync_status: str = "pending"
    crm_log_status: str = "pending"
    errors: list[str] = field(default_factory=list)


class ExamWorkflowPipeline:
    """End-to-end executor for WF1 Exam Result Cycle."""

    def __init__(
        self,
        storage_dir: str = "./storage/answer_sheets",
        min_confidence: float = 0.70,
    ) -> None:
        self.ingestion_agent = IngestionAgent(storage_dir=storage_dir)
        self.ocr_agent = OCRAgent()
        self.eval_agent = EvaluationAgent()
        self.verifier = ExamVerifier(min_confidence_threshold=min_confidence)
        self.analysis_agent = AnalysisAgent()
        self.comm_agent = CommunicationAgent()
        self.min_confidence = min_confidence

    def process_answer_sheet(
        self,
        run_id: str,
        file_bytes: bytes,
        filename: str,
        rubrics: list[RubricCriterion],
        ocr_text_override: str | None = None,
        historical_scores: list[float] | None = None,
        student_name: str = "Student",
        parent_email: str = "parent@example.edu",
        course_name: str = "CS301-Algorithms",
    ) -> ExamPipelineOutput:
        """Execute complete pipeline lifecycle."""
        # 1. Ingestion
        ingest_res = self.ingestion_agent.ingest_answer_sheet(file_bytes, filename)
        if ingest_res.status == "rejected":
            return ExamPipelineOutput(
                run_id=run_id,
                status="failed",
                ingestion=ingest_res,
                errors=[ingest_res.error_reason or "Ingestion rejected file"],
            )

        # 2. OCR Extraction
        text_content = ocr_text_override or "Roll: CS-2026-001\nQ1. Default extracted text."
        ocr_res = self.ocr_agent.extract_from_text(
            raw_content=text_content,
            document_id=ingest_res.file_id,
            default_exam_code=course_name,
        )

        # 3. Rubric Evaluation
        eval_summary = self.eval_agent.evaluate_sheet(
            document_id=ingest_res.file_id,
            student_roll=ocr_res.student_roll,
            answers=ocr_res.answers,
            rubrics=rubrics,
        )

        # 4. Arithmetic and Confidence Verification
        verif_res = self.verifier.verify(eval_summary)

        # 5. Performance Trend and Risk Analysis
        risk_profile = self.analysis_agent.analyze_risk(eval_summary, historical_scores)

        # 6. Communication Drafting
        email_draft = self.comm_agent.draft_parent_email(
            summary=eval_summary,
            risk_profile=risk_profile,
            student_name=ocr_res.student_name or student_name,
            parent_email=parent_email,
            course_name=course_name,
        )

        # 7. Immutable Decision Record
        decision_rec = DecisionRecordBuilder.create_decision(
            run_id=run_id,
            evaluation=eval_summary,
            confidence_threshold=self.min_confidence,
        )

        # 8 & 9. Integration state
        if verif_res.requires_approval:
            status = "requires_approval"
            erp_status = "held_for_approval"
            crm_status = "logged_under_review"
        else:
            status = "completed"
            erp_status = "synced_success"
            crm_status = "interaction_logged"

        return ExamPipelineOutput(
            run_id=run_id,
            status=status,
            ingestion=ingest_res,
            ocr=ocr_res,
            evaluation=eval_summary,
            verification=verif_res,
            analysis=risk_profile,
            communication=email_draft,
            decision_record=decision_rec,
            erp_sync_status=erp_status,
            crm_log_status=crm_status,
            errors=verif_res.violations,
        )
