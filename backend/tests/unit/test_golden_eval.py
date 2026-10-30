"""Golden dataset prompt evaluation suite.

TEST-04: LLM evaluation suite with golden dataset (50 answer sheets).
Asserts Mean Absolute Error (MAE <= 2.5), Pearson correlation >= 0.85, and verification bounds.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import pytest

from app.workflow.exam.evaluation import RubricCriterion
from app.workflow.exam.pipeline import ExamWorkflowPipeline

FIXTURE_PATH = Path(__file__).resolve().parent.parent / "fixtures" / "golden_dataset.json"


@pytest.fixture(scope="module")
def golden_dataset() -> list[dict]:
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def exam_rubrics() -> list[RubricCriterion]:
    return [
        RubricCriterion(
            question_num=1,
            max_marks=10.0,
            model_answer="Hash table hash function O(1) expected time key mapping",
            key_concepts=["hash table", "hash function", "o(1)"],
        ),
        RubricCriterion(
            question_num=2,
            max_marks=10.0,
            model_answer="QuickSort partition pivot divide and conquer recursive",
            key_concepts=["quicksort", "pivot", "partition"],
        ),
    ]


def test_golden_dataset_50_sheets_pipeline_accuracy(
    golden_dataset: list[dict],
    exam_rubrics: list[RubricCriterion],
) -> None:
    pipeline = ExamWorkflowPipeline()
    assert len(golden_dataset) == 50

    agent_totals: list[float] = []
    faculty_totals: list[float] = []
    absolute_errors: list[float] = []

    for entry in golden_dataset:
        run_id = f"eval_{entry['id']}"
        out = pipeline.process_answer_sheet(
            run_id=run_id,
            file_bytes=b"%PDF-1.4 Mock Sheet",
            filename=f"{entry['student_roll']}.pdf",
            rubrics=exam_rubrics,
            ocr_text_override=entry["raw_ocr_text"],
            course_name=entry["subject"],
        )

        assert out.evaluation is not None
        assert out.verification is not None
        assert out.verification.is_valid

        awarded = out.evaluation.total_marks_awarded
        faculty_score = entry["faculty_ground_truth"]["total_marks"]

        agent_totals.append(awarded)
        faculty_totals.append(faculty_score)
        absolute_errors.append(abs(awarded - faculty_score))

    # Calculate MAE
    mae = sum(absolute_errors) / len(absolute_errors)
    assert mae <= 2.5, f"MAE too high: {mae:.2f}"

    # Calculate Pearson Correlation
    n = len(agent_totals)
    mean_a = sum(agent_totals) / n
    mean_f = sum(faculty_totals) / n
    numerator = sum((a - mean_a) * (f - mean_f) for a, f in zip(agent_totals, faculty_totals))
    den_a = math.sqrt(sum((a - mean_a) ** 2 for a in agent_totals))
    den_f = math.sqrt(sum((f - mean_f) ** 2 for f in faculty_totals))
    correlation = numerator / (den_a * den_f) if den_a * den_f > 0 else 0.0

    assert correlation >= 0.85, f"Pearson correlation too low: {correlation:.3f}"
