"""Unit tests for Mock Enterprise Systems (ERP, LMS, CRM).

EPIC-11: Tests for standalone mock services:
- Campus ERP endpoints & chaos switch
- LMS courses, assignments, submissions, grading
- CRM contacts, tickets, Kanban pipeline, notes
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

# Add mock-systems directory to sys.path so tests can import mock modules
mock_root = Path(__file__).resolve().parent.parent.parent.parent / "mock-systems"
if str(mock_root) not in sys.path:
    sys.path.insert(0, str(mock_root))

from erp.app import app as erp_app
from lms.app import app as lms_app
from crm.app import app as crm_app


class TestCampusERPMock:
    @pytest.mark.asyncio
    async def test_health_check(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=erp_app), base_url="http://test") as client:
            resp = await client.get("/health")
            assert resp.status_code == 200
            assert resp.json()["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_get_students_and_filter_by_division(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=erp_app), base_url="http://test") as client:
            resp = await client.get("/api/students")
            assert resp.status_code == 200
            students = resp.json()
            assert len(students) >= 5

            # Filter by Division B (Riya Patel)
            resp_b = await client.get("/api/students?division=Division B")
            b_students = resp_b.json()
            assert any(s["name"] == "Riya Patel" for s in b_students)

    @pytest.mark.asyncio
    async def test_publish_marks(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=erp_app), base_url="http://test") as client:
            publish_data = {
                "subject_id": "sub_cs301",
                "marks": [{"student_id": "stu_b_001", "score": 88.0}],
                "published_by": "Test Agent",
            }
            resp = await client.post("/api/marks/publish", json=publish_data)
            assert resp.status_code == 200
            assert resp.json()["status"] == "published"

            # Verify mark was updated
            marks_resp = await client.get("/api/marks?student_id=stu_b_001&subject_id=sub_cs301")
            updated = marks_resp.json()
            assert updated[0]["score"] == 88.0

    @pytest.mark.asyncio
    async def test_chaos_switch_outage(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=erp_app), base_url="http://test") as client:
            # Activate chaos outage
            chaos_resp = await client.post("/_admin/chaos", json={"mode": "outage", "duration_s": 2.0})
            assert chaos_resp.status_code == 200

            # Normal endpoints return 503
            api_resp = await client.get("/api/students")
            assert api_resp.status_code == 503

            # Reset restores normal operation
            reset_resp = await client.post("/_admin/reset")
            assert reset_resp.status_code == 200
            restored_resp = await client.get("/api/students")
            assert restored_resp.status_code == 200


class TestLMSMock:
    @pytest.mark.asyncio
    async def test_courses_and_submissions(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=lms_app), base_url="http://test") as client:
            courses = (await client.get("/api/courses")).json()
            assert len(courses) >= 2

            subs = (await client.get("/api/submissions")).json()
            assert len(subs) >= 3

    @pytest.mark.asyncio
    async def test_grade_submission(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=lms_app), base_url="http://test") as client:
            grade_payload = {"submission_id": "subm_003", "grade": 48.5, "feedback": "Excellent work"}
            resp = await client.post("/api/grades", json=grade_payload)
            assert resp.status_code == 200
            assert resp.json()["grade"] == 48.5


class TestCRMMock:
    @pytest.mark.asyncio
    async def test_contacts_and_tickets(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=crm_app), base_url="http://test") as client:
            contacts = (await client.get("/api/contacts")).json()
            assert len(contacts) >= 3

            tickets = (await client.get("/api/tickets")).json()
            assert len(tickets) >= 2

    @pytest.mark.asyncio
    async def test_create_ticket_and_move_stage(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=crm_app), base_url="http://test") as client:
            # Create a ticket
            new_ticket = {
                "contact_id": "cnt_001",
                "title": "Follow up on attendance",
                "priority": "high",
                "stage": "New",
            }
            create_resp = await client.post("/api/tickets", json=new_ticket)
            assert create_resp.status_code == 200
            ticket_id = create_resp.json()["id"]

            # Move stage to In Progress
            move_resp = await client.post("/api/pipeline/move", json={"ticket_id": ticket_id, "new_stage": "In Progress"})
            assert move_resp.status_code == 200
            assert move_resp.json()["new_stage"] == "In Progress"
