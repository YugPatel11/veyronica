"""Exam Workflow API Router (EPIC-15-T08).

Provides HTTP endpoints to trigger, monitor, and query WF1 exam cycle executions.
"""

from __future__ import annotations

import base64
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.workflow.exam.pipeline import ExamWorkflowPipeline
from app.workflow.exam.evaluation import RubricCriterion

router = APIRouter(prefix="/exam-workflow", tags=["Exam Workflow"])

pipeline_instance = ExamWorkflowPipeline()


class RubricInput(BaseModel):
    question_num: int
    max_marks: float
    model_answer: str = ""
    key_concepts: list[str] = Field(default_factory=list)


class ExamProcessRequest(BaseModel):
    run_id: str
    filename: str = "sheet.pdf"
    file_base64: str | None = None
    raw_ocr_text: str | None = None
    course_name: str = "CS301-Algorithms"
    student_name: str = "Student"
    parent_email: str = "parent@example.edu"
    historical_scores: list[float] | None = None
    rubrics: list[RubricInput] = Field(default_factory=list)


@router.post("/process", status_code=status.HTTP_200_OK)
async def process_exam_submission(payload: ExamProcessRequest) -> dict[str, Any]:
    """Execute end-to-end exam grading pipeline on submitted answer sheet."""
    # Decode base64 or fallback to mock pdf bytes
    if payload.file_base64:
        try:
            file_bytes = base64.b64decode(payload.file_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64 encoding: {e}")
    else:
        file_bytes = b"%PDF-1.4 Mock Exam Sheet"

    rubric_objects = [
        RubricCriterion(
            question_num=r.question_num,
            max_marks=r.max_marks,
            model_answer=r.model_answer,
            key_concepts=r.key_concepts,
        )
        for r in payload.rubrics
    ] or [
        RubricCriterion(
            question_num=1,
            max_marks=10.0,
            model_answer="Algorithm explanation",
            key_concepts=["algorithm", "complexity"],
        )
    ]

    result = pipeline_instance.process_answer_sheet(
        run_id=payload.run_id,
        file_bytes=file_bytes,
        filename=payload.filename,
        rubrics=rubric_objects,
        ocr_text_override=payload.raw_ocr_text,
        historical_scores=payload.historical_scores,
        student_name=payload.student_name,
        parent_email=payload.parent_email,
        course_name=payload.course_name,
    )

    return {
        "run_id": result.run_id,
        "status": result.status,
        "erp_sync_status": result.erp_sync_status,
        "crm_log_status": result.crm_log_status,
        "marks_awarded": result.evaluation.total_marks_awarded if result.evaluation else 0.0,
        "total_max_marks": result.evaluation.total_max_marks if result.evaluation else 0.0,
        "percentage": result.evaluation.percentage if result.evaluation else 0.0,
        "risk_level": result.analysis.risk_level.value if result.analysis else "low",
        "requires_approval": result.verification.requires_approval if result.verification else False,
        "decision_hash": result.decision_record.decision_hash if result.decision_record else "",
        "email_subject": result.communication.subject if result.communication else "",
        "violations": result.errors,
    }
