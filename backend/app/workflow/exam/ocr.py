"""OCR and Vision Extraction Agent for Exam Answer Sheets (EPIC-15-T02).

Extracts student identity, question numbers, extracted answer text, and
per-question recognition confidence from ingested documents.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExtractedAnswer:
    question_num: int
    question_subpart: str | None
    extracted_text: str
    ocr_confidence: float  # 0.0 to 1.0
    bounding_box: dict[str, int] | None = None


@dataclass
class OCRExtractionResult:
    document_id: str
    student_roll: str
    student_name: str | None
    exam_code: str
    answers: list[ExtractedAnswer]
    raw_text: str
    average_confidence: float


class OCRAgent:
    """Extracts structured questions and answers from exam answer sheets using OCR/Vision simulation."""

    def extract_from_text(
        self,
        raw_content: str,
        document_id: str,
        default_exam_code: str = "EXAM-2026-CS",
    ) -> OCRExtractionResult:
        """Parse structured answers from raw text or OCR pipeline output."""
        # Extract roll number pattern (e.g. ROLL: CS2024-001 or Roll No: 12345)
        roll_match = re.search(r"(?:roll(?:\s*no)?[:\s]+)([A-Z0-9\-]+)", raw_content, re.IGNORECASE)
        student_roll = roll_match.group(1) if roll_match else "UNKNOWN_ROLL"

        name_match = re.search(r"(?:name[:\s]+)([A-Za-z\s]+)(?:\n|$)", raw_content, re.IGNORECASE)
        student_name = name_match.group(1).strip() if name_match else None

        exam_match = re.search(r"(?:exam|course|subject)[:\s]+([A-Z0-9\-]+)", raw_content, re.IGNORECASE)
        exam_code = exam_match.group(1) if exam_match else default_exam_code

        # Parse questions e.g. Q1. ... or Q2) ... or Question 1: ...
        q_pattern = re.compile(
            r"(?:Q(?:uestion)?\s*(\d+)(?:\s*([a-zA-Z]))?[\.\:\)\-]\s*)(.*?)(?=(?:Q(?:uestion)?\s*\d+[\.\:\)\-]|\Z))",
            re.DOTALL | re.IGNORECASE,
        )

        matches = list(q_pattern.finditer(raw_content))
        extracted_answers: list[ExtractedAnswer] = []

        if matches:
            for m in matches:
                q_num = int(m.group(1))
                subpart = m.group(2) if m.group(2) else None
                ans_text = m.group(3).strip()
                # Basic confidence estimation based on text length and character validity
                clean_ratio = len(re.findall(r"[A-Za-z0-9\s\.\,\;\:\?\!]", ans_text)) / max(len(ans_text), 1)
                confidence = round(min(0.98, max(0.50, clean_ratio)), 2)

                extracted_answers.append(
                    ExtractedAnswer(
                        question_num=q_num,
                        question_subpart=subpart,
                        extracted_text=ans_text,
                        ocr_confidence=confidence,
                    )
                )
        else:
            # Fallback if no explicit Q patterns found
            extracted_answers.append(
                ExtractedAnswer(
                    question_num=1,
                    question_subpart=None,
                    extracted_text=raw_content.strip(),
                    ocr_confidence=0.85,
                )
            )

        avg_conf = (
            round(sum(a.ocr_confidence for a in extracted_answers) / len(extracted_answers), 2)
            if extracted_answers
            else 0.0
        )

        return OCRExtractionResult(
            document_id=document_id,
            student_roll=student_roll,
            student_name=student_name,
            exam_code=exam_code,
            answers=extracted_answers,
            raw_text=raw_content,
            average_confidence=avg_conf,
        )
