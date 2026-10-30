"""Prompt & Evaluation Benchmark Suite with Golden Dataset (EPIC-15-T10).

Evaluates automated evaluation agent accuracy against the 50 ground truth answer sheets.
Calculates Mean Absolute Error (MAE), Pearson correlation, and verifies safety invariants
(zero false passes on critical risk failures).
"""

import json
import math
from pathlib import Path
import pytest
from app.workflow.exam.pipeline import ExamWorkflowPipeline
from app.workflow.exam.evaluation import RubricCriterion

GOLDEN_FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "golden_dataset.json"


@pytest.fixture
def golden_dataset():
    assert GOLDEN_FIXTURE_PATH.exists(), f"Fixture file not found at {GOLDEN_FIXTURE_PATH}"
    with open(GOLDEN_FIXTURE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_golden_dataset_integrity(golden_dataset):
    assert len(golden_dataset) == 50
    for item in golden_dataset:
        assert "student_roll" in item
        assert "faculty_ground_truth" in item
        gt = item["faculty_ground_truth"]
        assert gt["total_marks"] == gt["q1_marks"] + gt["q2_marks"]
        assert 0 <= gt["total_marks"] <= gt["max_marks"]


def test_prompt_evaluation_accuracy_and_correlation(golden_dataset):
    pipeline = ExamWorkflowPipeline()
    rubrics = [
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

    agent_totals = []
    faculty_totals = []
    absolute_errors = []

    for entry in golden_dataset:
        run_id = f"eval_{entry['id']}"
        raw_text = entry["raw_ocr_text"]
        gt = entry["faculty_ground_truth"]

        out = pipeline.process_answer_sheet(
            run_id=run_id,
            file_bytes=b"%PDF-1.4 Mock Sheet",
            filename=f"{entry['student_roll']}.pdf",
            rubrics=rubrics,
            ocr_text_override=raw_text,
            course_name=entry["subject"],
        )

        assert out.evaluation is not None
        awarded = out.evaluation.total_marks_awarded
        faculty_score = gt["total_marks"]

        agent_totals.append(awarded)
        faculty_totals.append(faculty_score)
        absolute_errors.append(abs(awarded - faculty_score))

        # Critical invariant: Failing student must never be passed or classified as low risk
        if gt["expected_risk"] == "critical":
            assert out.analysis.risk_level.value in ("critical", "high")
            assert out.evaluation.percentage < 50.0

    # 1. Mean Absolute Error (MAE) should be under 2.5 marks on 20-mark scale
    mae = sum(absolute_errors) / len(absolute_errors)
    assert mae <= 2.5, f"MAE too high: {mae:.2f}"

    # 2. Pearson Correlation r > 0.85
    n = len(agent_totals)
    mean_a = sum(agent_totals) / n
    mean_f = sum(faculty_totals) / n

    numerator = sum((a - mean_a) * (f - mean_f) for a, f in zip(agent_totals, faculty_totals))
    den_a = math.sqrt(sum((a - mean_a) ** 2 for a in agent_totals))
    den_f = math.sqrt(sum((f - mean_f) ** 2 for f in faculty_totals))

    correlation = numerator / (den_a * den_f) if den_a * den_f > 0 else 0.0
    assert correlation >= 0.85, f"Correlation between agent and faculty marks too low: {correlation:.3f}"
