"""Evaluation Agent: marking against rubric with confidence (EPIC-15-T03).

Grades extracted student answers using rubric guidelines, matching key concepts,
calculating awarded marks, and estimating evaluation confidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from .ocr import ExtractedAnswer


@dataclass
class RubricCriterion:
    question_num: int
    max_marks: float
    model_answer: str
    key_concepts: list[str]
    partial_marking_rules: dict[str, float] = field(default_factory=dict)


@dataclass
class QuestionEvaluation:
    question_num: int
    marks_awarded: float
    max_marks: float
    confidence: float
    feedback: str
    matched_concepts: list[str]
    missing_concepts: list[str]


@dataclass
class EvaluationSummary:
    document_id: str
    student_roll: str
    total_marks_awarded: float
    total_max_marks: float
    percentage: float
    evaluations: list[QuestionEvaluation]
    overall_confidence: float


class EvaluationAgent:
    """Evaluates student answers against structured rubrics."""

    def evaluate_question(
        self,
        answer: ExtractedAnswer,
        rubric: RubricCriterion,
    ) -> QuestionEvaluation:
        """Mark a single question answer against its rubric criterion."""
        text_lower = answer.extracted_text.lower()
        matched = []
        missing = []

        concept_scores: list[float] = []
        for concept in rubric.key_concepts:
            c_low = concept.lower()
            stem = c_low[:-3] if c_low.endswith("ing") else (c_low[:-2] if c_low.endswith("ed") else c_low.rstrip("s"))
            if c_low in text_lower or (len(stem) >= 4 and stem in text_lower):
                matched.append(concept)
                concept_scores.append(1.0)
            else:
                words = [w for w in c_low.split() if len(w) > 3]
                matched_words = [w for w in words if w in text_lower or (len(w) > 5 and w[:4] in text_lower)]
                if words and len(matched_words) > 0:
                    matched.append(concept)
                    concept_scores.append(len(matched_words) / len(words))
                else:
                    missing.append(concept)
                    concept_scores.append(0.0)

        total_concepts = len(rubric.key_concepts)
        if total_concepts > 0:
            match_ratio = sum(concept_scores) / total_concepts
            marks = round(match_ratio * rubric.max_marks, 1)
        else:
            marks = rubric.max_marks if len(answer.extracted_text) > 10 else 0.0
            match_ratio = 1.0 if marks > 0 else 0.0

        # Confidence combines OCR quality and concept match clarity
        confidence = round(0.5 * answer.ocr_confidence + 0.5 * (0.8 + 0.2 * match_ratio), 2)
        confidence = min(0.99, max(0.40, confidence))

        feedback = (
            f"Awarded {marks}/{rubric.max_marks}. "
            f"Covered concepts: {', '.join(matched) if matched else 'None'}. "
            f"Missing key elements: {', '.join(missing) if missing else 'None'}."
        )

        return QuestionEvaluation(
            question_num=rubric.question_num,
            marks_awarded=marks,
            max_marks=rubric.max_marks,
            confidence=confidence,
            feedback=feedback,
            matched_concepts=matched,
            missing_concepts=missing,
        )

    def evaluate_sheet(
        self,
        document_id: str,
        student_roll: str,
        answers: list[ExtractedAnswer],
        rubrics: list[RubricCriterion],
    ) -> EvaluationSummary:
        """Evaluate full answer sheet against all rubric criteria."""
        rubric_map = {r.question_num: r for r in rubrics}
        evaluations: list[QuestionEvaluation] = []

        for ans in answers:
            rubric = rubric_map.get(ans.question_num)
            if rubric:
                eval_item = self.evaluate_question(ans, rubric)
                evaluations.append(eval_item)
            else:
                # Default rubric if question wasn't mapped
                default_rubric = RubricCriterion(
                    question_num=ans.question_num,
                    max_marks=5.0,
                    model_answer="",
                    key_concepts=[],
                )
                evaluations.append(self.evaluate_question(ans, default_rubric))

        total_awarded = round(sum(e.marks_awarded for e in evaluations), 1)
        total_max = sum(e.max_marks for e in evaluations) or 1.0
        pct = round((total_awarded / total_max) * 100, 1)
        avg_conf = (
            round(sum(e.confidence for e in evaluations) / len(evaluations), 2)
            if evaluations
            else 0.8
        )

        return EvaluationSummary(
            document_id=document_id,
            student_roll=student_roll,
            total_marks_awarded=total_awarded,
            total_max_marks=total_max,
            percentage=pct,
            evaluations=evaluations,
            overall_confidence=avg_conf,
        )
