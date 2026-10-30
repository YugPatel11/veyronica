"""Unit tests for Phase 5 Advanced Workflows.

EPIC-26: Timetable Generation & Constraint Satisfaction Solver.
EPIC-27: Question Paper Generation, Bloom's Taxonomy Balance, and Marking Schemes.
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app
from app.workflow.question_paper_generator import (
    BloomLevel,
    DifficultyLevel,
    QuestionPaperGenerator,
)
from app.workflow.timetable_solver import (
    Classroom,
    CourseSession,
    TimetableSolver,
)


class TestTimetableSolver:
    """EPIC-26: Tests for CSP Timetable Scheduler."""

    def test_basic_feasible_schedule(self):
        solver = TimetableSolver()
        sessions = [
            CourseSession("s1", "CS301", "DBMS", "prof_priya", "Div-A", 45),
            CourseSession("s2", "CS201", "DSA", "prof_arjun", "Div-A", 40),
            CourseSession("s3", "PHY101", "Physics", "dr_nair", "Div-B", 35),
        ]
        result = solver.solve(sessions)

        assert result.success is True
        assert result.total_slots_needed == 3
        assert result.total_slots_assigned == 3
        assert len(result.conflicts) == 0
        assert len(result.schedule) == 3

        # Verify no double booking of same faculty in same slot
        seen_faculty_slots: set[tuple[str, int, str]] = set()
        for slot in result.schedule:
            key = (slot.day, slot.period, slot.session.faculty_id)
            assert key not in seen_faculty_slots
            seen_faculty_slots.add(key)

    def test_classroom_capacity_enforcement(self):
        # Only small rooms (capacity 30)
        rooms = [Classroom("R1", "Small-Room-1", 30)]
        solver = TimetableSolver(classrooms=rooms)

        # Session needs 60 seats -> impossible
        large_session = [CourseSession("s_large", "CS301", "Big Lecture", "prof_a", "Div-A", 60)]
        result = solver.solve(large_session)

        assert result.success is False
        assert result.total_slots_assigned == 0
        assert len(result.conflicts) > 0
        assert any("capacity" in c.lower() for c in result.conflicts)

    def test_faculty_unavailability_constraint(self):
        # prof_x is unavailable on Monday Period 1
        rooms = [Classroom("R1", "Room-1", 60)]
        solver = TimetableSolver(
            classrooms=rooms,
            days=["Monday"],
            periods=[1, 2],
            faculty_unavailability={"prof_x": [("Monday", 1)]},
        )

        session = [CourseSession("s1", "CS101", "Intro", "prof_x", "Div-A", 40)]
        result = solver.solve(session)

        assert result.success is True
        assert len(result.schedule) == 1
        assert result.schedule[0].day == "Monday"
        assert result.schedule[0].period == 2  # Period 1 avoided


class TestQuestionPaperGenerator:
    """EPIC-27: Tests for Bloom Taxonomy Question Paper Synthesis."""

    def test_generate_50_marks_paper(self):
        generator = QuestionPaperGenerator()
        paper = generator.generate(course_code="CS301", course_name="DBMS", total_marks_target=50)

        assert paper.course_code == "CS301"
        assert paper.total_marks == 50
        assert paper.is_valid_coverage is True
        assert len(paper.questions) == 5

        # Check Bloom level classifications
        bloom_keys = set(paper.bloom_distribution.keys())
        assert BloomLevel.UNDERSTAND.value in bloom_keys
        assert BloomLevel.APPLY.value in bloom_keys

        # Check difficulty distributions
        diff_keys = set(paper.difficulty_distribution.keys())
        assert DifficultyLevel.MEDIUM.value in diff_keys

        # Originality and rubrics
        for q in paper.questions:
            assert q.originality_score >= 0.90
            assert len(q.answer_key) > 10
            assert len(q.rubric_criteria) >= 2

    def test_question_paper_unit_coverage(self):
        generator = QuestionPaperGenerator()
        paper = generator.generate(course_code="CS301", total_marks_target=50)

        # Must span across multiple units
        assert len(paper.unit_coverage) >= 2
        assert any("Unit 1" in unit for unit in paper.unit_coverage)
        assert any("Unit 2" in unit for unit in paper.unit_coverage)


class TestAdvancedWorkflowEndpoints:
    """EPIC-26 & EPIC-27: Tests for REST API routes."""

    @pytest.mark.asyncio
    async def test_timetable_generate_api(self):
        app = create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post(
                "/api/v1/advanced-workflows/timetable/generate",
                json={
                    "sessions": [
                        {
                            "id": "s1",
                            "course_code": "CS301",
                            "course_name": "Database Systems",
                            "faculty_id": "prof_priya",
                            "division": "Div-A",
                            "student_count": 40,
                        }
                    ]
                },
            )
            assert res.status_code == 200
            data = res.json()
            assert data["success"] is True
            assert data["total_slots_assigned"] == 1
            assert len(data["schedule"]) == 1
            assert data["schedule"][0]["course_code"] == "CS301"

    @pytest.mark.asyncio
    async def test_question_paper_generate_api(self):
        app = create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post(
                "/api/v1/advanced-workflows/question-paper/generate",
                json={
                    "course_code": "CS301",
                    "course_name": "Database Systems Engineering",
                    "total_marks": 50,
                },
            )
            assert res.status_code == 200
            data = res.json()
            assert data["course_code"] == "CS301"
            assert data["total_marks"] == 50
            assert data["is_valid_coverage"] is True
            assert len(data["questions"]) > 0
            assert "bloom_distribution" in data
            assert "difficulty_distribution" in data
