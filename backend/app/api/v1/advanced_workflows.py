"""Advanced Workflow API endpoints for Timetable and Question Paper Generation.

EPIC-26: WF5 Timetable solver API.
EPIC-27: WF6 Question paper generation API.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.workflow.question_paper_generator import generator as qp_generator
from app.workflow.timetable_solver import (
    Classroom,
    CourseSession,
    TimetableSolver,
)

router = APIRouter(prefix="/advanced-workflows", tags=["Advanced Workflows"])


# ── Request / Response Models ────────────────────────────────────────────────

class TimetableGenerateRequest(BaseModel):
    sessions: list[dict[str, Any]] = Field(default_factory=list)
    classrooms: list[dict[str, Any]] = Field(default_factory=list)
    faculty_unavailability: dict[str, list[tuple[str, int]]] = Field(default_factory=dict)


class QuestionPaperGenerateRequest(BaseModel):
    course_code: str = "CS301"
    course_name: str = "Database Systems Engineering"
    total_marks: int = 50


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/timetable/generate")
async def generate_timetable(body: TimetableGenerateRequest) -> dict[str, Any]:
    """EPIC-26-T03: Generate timetable schedule with constraint satisfaction."""
    custom_rooms = [
        Classroom(id=r["id"], name=r["name"], capacity=int(r["capacity"]))
        for r in body.classrooms
    ] if body.classrooms else None

    solver_instance = TimetableSolver(
        classrooms=custom_rooms,
        faculty_unavailability=body.faculty_unavailability,
    )

    default_sessions = [
        CourseSession("s1", "CS301", "Database Systems", "prof_priya", "Div-A", 50),
        CourseSession("s2", "CS201", "Data Structures", "prof_arjun", "Div-A", 45),
        CourseSession("s3", "PHY101", "Physics Lab", "dr_nair", "Div-B", 35),
        CourseSession("s4", "CS301", "Database Systems Lab", "prof_priya", "Div-A", 38),
        CourseSession("s5", "MA201", "Discrete Math", "dr_verma", "Div-B", 55),
    ]

    target_sessions = [
        CourseSession(
            id=s["id"],
            course_code=s["course_code"],
            course_name=s["course_name"],
            faculty_id=s["faculty_id"],
            division=s["division"],
            student_count=int(s.get("student_count", 40)),
        )
        for s in body.sessions
    ] if body.sessions else default_sessions

    result = solver_instance.solve(target_sessions)

    return {
        "success": result.success,
        "total_slots_needed": result.total_slots_needed,
        "total_slots_assigned": result.total_slots_assigned,
        "conflicts": result.conflicts,
        "schedule": [
            {
                "day": slot.day,
                "period": slot.period,
                "course_code": slot.session.course_code,
                "course_name": slot.session.course_name,
                "faculty_id": slot.session.faculty_id,
                "division": slot.session.division,
                "room": slot.classroom.name,
                "room_id": slot.classroom.id,
            }
            for slot in result.schedule
        ],
    }


@router.post("/question-paper/generate")
async def generate_question_paper(body: QuestionPaperGenerateRequest) -> dict[str, Any]:
    """EPIC-27-T02 / T04: Generate syllabus-aligned question paper."""
    res = qp_generator.generate(
        course_code=body.course_code,
        course_name=body.course_name,
        total_marks_target=body.total_marks,
    )

    return {
        "course_code": res.course_code,
        "course_name": res.course_name,
        "total_marks": res.total_marks,
        "is_valid_coverage": res.is_valid_coverage,
        "bloom_distribution": res.bloom_distribution,
        "difficulty_distribution": res.difficulty_distribution,
        "unit_coverage": res.unit_coverage,
        "questions": [
            {
                "id": q.id,
                "unit": q.unit,
                "question_text": q.question_text,
                "marks": q.marks,
                "bloom_level": q.bloom_level.value,
                "difficulty": q.difficulty.value,
                "answer_key": q.answer_key,
                "rubric_criteria": q.rubric_criteria,
                "originality_score": q.originality_score,
            }
            for q in res.questions
        ],
    }
