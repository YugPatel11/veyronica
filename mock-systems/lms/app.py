"""LMS Mock Service (Port 8102).

EPIC-11-T02: LMS service (FastAPI + lms_db).
Endpoints match backend/app/connectors/lms.py.
"""

from __future__ import annotations

import copy
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

import sys
from pathlib import Path

_MOCK_ROOT = Path(__file__).resolve().parent.parent
if str(_MOCK_ROOT) not in sys.path:
    sys.path.insert(0, str(_MOCK_ROOT))

from shared.chaos import ChaosMiddleware, chaos_state
from shared.data import ASSIGNMENTS, COURSES, SUBMISSIONS

app = FastAPI(title="LMS Mock Service", version="0.1.0")
app.add_middleware(ChaosMiddleware)

courses_db = copy.deepcopy(COURSES)
assignments_db = copy.deepcopy(ASSIGNMENTS)
submissions_db = copy.deepcopy(SUBMISSIONS)


class ChaosRequest(BaseModel):
    mode: str = "outage"
    duration_s: float = 30.0
    latency_ms: int = 2000
    error_rate: float = 0.5


class GradeSubmissionRequest(BaseModel):
    submission_id: str
    grade: float
    feedback: str = ""
    graded_by: str = "NEXUS Agent"


class CreateAssignmentRequest(BaseModel):
    course_id: str
    title: str
    due_date: str
    max_points: int = 100


# ── Health & Admin ───────────────────────────────────────────────────────────

@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "lms", "timestamp": datetime.now(UTC).isoformat()}


@app.post("/_admin/chaos")
async def trigger_chaos(body: ChaosRequest) -> dict[str, Any]:
    return chaos_state.activate(body.mode, body.duration_s, latency_ms=body.latency_ms, error_rate=body.error_rate)


@app.post("/_admin/reset")
async def reset_state() -> dict[str, str]:
    global courses_db, assignments_db, submissions_db
    courses_db = copy.deepcopy(COURSES)
    assignments_db = copy.deepcopy(ASSIGNMENTS)
    submissions_db = copy.deepcopy(SUBMISSIONS)
    chaos_state.reset()
    return {"status": "reset_complete"}


# ── LMS API Endpoints ────────────────────────────────────────────────────────

@app.get("/api/courses")
async def get_courses() -> list[dict[str, Any]]:
    return courses_db


@app.get("/api/courses/{course_id}")
async def get_course(course_id: str) -> dict[str, Any]:
    c = next((item for item in courses_db if item["id"] == course_id), None)
    if not c:
        raise HTTPException(status_code=404, detail="Course not found")
    return c


@app.get("/api/assignments")
async def get_assignments(course_id: str | None = Query(None)) -> list[dict[str, Any]]:
    if course_id:
        return [a for a in assignments_db if a.get("course_id") == course_id]
    return assignments_db


@app.post("/api/assignments")
async def create_assignment(body: CreateAssignmentRequest) -> dict[str, Any]:
    new_asg = {
        "id": f"asg_{len(assignments_db) + 1:03d}",
        "course_id": body.course_id,
        "title": body.title,
        "due_date": body.due_date,
        "max_points": body.max_points,
    }
    assignments_db.append(new_asg)
    return new_asg


@app.get("/api/submissions")
async def get_submissions(
    assignment_id: str | None = Query(None),
    student_id: str | None = Query(None),
) -> list[dict[str, Any]]:
    results = submissions_db
    if assignment_id:
        results = [s for s in results if s.get("assignment_id") == assignment_id]
    if student_id:
        results = [s for s in results if s.get("student_id") == student_id]
    return results


@app.get("/api/submissions/{submission_id}")
async def get_submission(submission_id: str) -> dict[str, Any]:
    sub = next((s for s in submissions_db if s["id"] == submission_id), None)
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    return sub


@app.post("/api/grades")
async def submit_grade(body: GradeSubmissionRequest) -> dict[str, Any]:
    sub = next((s for s in submissions_db if s["id"] == body.submission_id), None)
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    sub["grade"] = body.grade
    sub["feedback"] = body.feedback
    sub["status"] = "graded"
    sub["graded_at"] = datetime.now(UTC).isoformat()
    return {"status": "graded", "submission_id": body.submission_id, "grade": body.grade}


# ── Web UI ───────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def lms_ui() -> str:
    courses_html = "".join(f"<li><b>{c['code']}:</b> {c['name']} (Instructor: {c['instructor']})</li>" for c in courses_db)
    subs_html = "".join(
        f"<tr><td>{s['id']}</td><td>{s['assignment_id']}</td><td>{s['student_id']}</td><td>{s['status']}</td><td>{s.get('grade', '-')}</td></tr>"
        for s in submissions_db
    )
    return f"""<!DOCTYPE html>
<html>
<head>
  <title>LMS — Standalone Mock</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 2rem; background: #FAF9F6; color: #1E2A32; }}
    h1 {{ color: #1F3F8C; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; background: #FFF; border: 1px solid #D9D2C2; }}
    th, td {{ padding: 8px 12px; text-align: left; border-bottom: 1px solid #E9E4D8; }}
    th {{ background: #F2EEE5; }}
  </style>
</head>
<body>
  <h1>LMS — Standalone Mock Service (:8102)</h1>
  <h2>Courses</h2>
  <ul>{courses_html}</ul>
  <h2>Student Submissions & Gradebook</h2>
  <table>
    <tr><th>ID</th><th>Assignment</th><th>Student</th><th>Status</th><th>Grade</th></tr>
    {subs_html}
  </table>
</body>
</html>"""
