import tempfile
from pathlib import Path
import pytest
from app.workflow.exam import (
    IngestionAgent,
    OCRAgent,
    EvaluationAgent,
    ExamVerifier,
    DecisionRecordBuilder,
    RubricCriterion,
    ExtractedAnswer,
)


@pytest.fixture
def temp_storage():
    with tempfile.TemporaryDirectory() as d:
        yield d


def test_ingestion_agent_valid_pdf(temp_storage):
    agent = IngestionAgent(storage_dir=temp_storage)
    pdf_content = b"%PDF-1.4 test document content"
    res = agent.ingest_answer_sheet(pdf_content, "student_01.pdf")

    assert res.status == "accepted"
    assert res.mime_type == "application/pdf"
    assert res.size_bytes == len(pdf_content)
    assert Path(res.storage_path).exists()
    assert len(res.sha256_hash) == 64


def test_ingestion_agent_rejects_empty_and_invalid(temp_storage):
    agent = IngestionAgent(storage_dir=temp_storage)

    # Empty
    res_empty = agent.ingest_answer_sheet(b"", "empty.pdf")
    assert res_empty.status == "rejected"
    assert "empty" in res_empty.error_reason.lower()

    # Invalid header
    res_invalid = agent.ingest_answer_sheet(b"BAD_HEADER_DATA", "corrupt.png")
    assert res_invalid.status == "rejected"
    assert "unsupported" in res_invalid.error_reason.lower()


def test_ocr_extraction_agent():
    ocr = OCRAgent()
    raw_sheet = """
    Roll No: CS-2026-042
    Name: Aarav Sharma
    Exam: CS301-Algorithms

    Q1. A hash table provides O(1) average time complexity for insertions and lookups using a hash function.
    Q2. QuickSort operates on divide and conquer principle, partitioning array around a chosen pivot element.
    """
    extracted = ocr.extract_from_text(raw_sheet, document_id="doc_101")

    assert extracted.student_roll == "CS-2026-042"
    assert extracted.student_name == "Aarav Sharma"
    assert len(extracted.answers) == 2
    assert extracted.answers[0].question_num == 1
    assert "hash table" in extracted.answers[0].extracted_text.lower()
    assert extracted.average_confidence >= 0.70


def test_evaluation_agent_and_decision_records():
    eval_agent = EvaluationAgent()
    rubrics = [
        RubricCriterion(
            question_num=1,
            max_marks=10.0,
            model_answer="Hash table O(1) complexity hash function",
            key_concepts=["hash table", "o(1)", "hash function"],
        ),
        RubricCriterion(
            question_num=2,
            max_marks=10.0,
            model_answer="Divide and conquer partitioning around pivot",
            key_concepts=["divide and conquer", "pivot", "partitioning"],
        ),
    ]

    answers = [
        ExtractedAnswer(
            question_num=1,
            question_subpart=None,
            extracted_text="A hash table uses a hash function to achieve O(1) average lookup.",
            ocr_confidence=0.92,
        ),
        ExtractedAnswer(
            question_num=2,
            question_subpart=None,
            extracted_text="QuickSort partitions the array around a pivot element using divide and conquer.",
            ocr_confidence=0.90,
        ),
    ]

    summary = eval_agent.evaluate_sheet("doc_101", "CS-2026-042", answers, rubrics)

    assert summary.total_marks_awarded == 20.0
    assert summary.total_max_marks == 20.0
    assert summary.percentage == 100.0
    assert summary.overall_confidence >= 0.80

    # Decision Record
    decision = DecisionRecordBuilder.create_decision("run_test_001", summary, confidence_threshold=0.70)
    assert decision.selected_option_id == "opt_auto_publish"
    assert not decision.requires_human_approval
    assert len(decision.decision_hash) == 64


def test_exam_verifier_success_and_violations():
    eval_agent = EvaluationAgent()
    rubrics = [
        RubricCriterion(
            question_num=1,
            max_marks=10.0,
            model_answer="",
            key_concepts=["compiler", "syntax"],
        )
    ]
    answers = [
        ExtractedAnswer(
            question_num=1,
            question_subpart=None,
            extracted_text="A compiler analyzes syntax.",
            ocr_confidence=0.95,
        )
    ]
    summary = eval_agent.evaluate_sheet("doc_102", "CS-2026-099", answers, rubrics)

    verifier = ExamVerifier(min_confidence_threshold=0.70)
    v_result = verifier.verify(summary)

    assert v_result.is_valid is True
    assert v_result.sum_matches is True
    assert v_result.ranges_valid is True
    assert v_result.requires_approval is False

    # Intentionally corrupt summary total to trigger verifier failure
    summary.total_marks_awarded = 999.0
    v_corrupt = verifier.verify(summary)
    assert v_corrupt.is_valid is False
    assert v_corrupt.sum_matches is False
    assert v_corrupt.requires_approval is True
    assert any("mismatch" in s.lower() for s in v_corrupt.violations)
