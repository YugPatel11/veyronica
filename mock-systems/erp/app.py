"""Campus ERP Mock Service (Port 8101).

EPIC-11-T01: Campus ERP service (FastAPI + erp_db + API key auth).
Endpoints match backend/app/connectors/erp.py.
"""

from __future__ import annotations

import copy
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

import sys
from pathlib import Path

_MOCK_ROOT = Path(__file__).resolve().parent.parent
if str(_MOCK_ROOT) not in sys.path:
    sys.path.insert(0, str(_MOCK_ROOT))

from shared.chaos import ChaosMiddleware, chaos_state
from shared.data import DIVISIONS, FACULTY, MARKS, STUDENTS, SUBJECTS

app = FastAPI(title="Campus ERP Mock Service", version="0.1.0")
app.add_middleware(ChaosMiddleware)

# In-memory store initialised from seed data
students_db = copy.deepcopy(STUDENTS)
marks_db = copy.deepcopy(MARKS)
subjects_db = copy.deepcopy(SUBJECTS)
divisions_db = copy.deepcopy(DIVISIONS)
faculty_db = copy.deepcopy(FACULTY)
mark_history_db: list[dict[str, Any]] = []


# ── Chaos Request Model ──────────────────────────────────────────────────────

class ChaosRequest(BaseModel):
    mode: str = "outage"  # outage, latency, error_rate
    duration_s: float = 30.0
    latency_ms: int = 2000
    error_rate: float = 0.5


class PublishMarksRequest(BaseModel):
    subject_id: str
    marks: list[dict[str, Any]] = Field(default_factory=list)
    published_by: str = "NEXUS Agent"


# ── Admin & Health ───────────────────────────────────────────────────────────

@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "campus-erp", "timestamp": datetime.now(UTC).isoformat()}


@app.post("/_admin/chaos")
async def trigger_chaos(body: ChaosRequest) -> dict[str, Any]:
    return chaos_state.activate(body.mode, body.duration_s, latency_ms=body.latency_ms, error_rate=body.error_rate)


@app.post("/_admin/reset")
async def reset_state() -> dict[str, str]:
    global students_db, marks_db
    students_db = copy.deepcopy(STUDENTS)
    marks_db = copy.deepcopy(MARKS)
    chaos_state.reset()
    return {"status": "reset_complete"}


# ── ERP API Endpoints ────────────────────────────────────────────────────────

@app.get("/api/students")
async def get_students(division: str | None = Query(None)) -> list[dict[str, Any]]:
    if division:
        return [s for s in students_db if s.get("division") == division or s.get("division_id") == division]
    return [s for s in students_db if s.get("is_active", True)]


@app.get("/api/students/{student_id}")
async def get_student(student_id: str) -> dict[str, Any]:
    student = next((s for s in students_db if s["id"] == student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.put("/api/students/{student_id}")
async def update_student(student_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    student = next((s for s in students_db if s["id"] == student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student.update(payload)
    return student


@app.delete("/api/students/{student_id}")
async def delete_student(student_id: str) -> dict[str, str]:
    student = next((s for s in students_db if s["id"] == student_id), None)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student["is_active"] = False
    return {"status": "soft_deleted", "student_id": student_id}


@app.get("/api/subjects")
async def get_subjects() -> list[dict[str, Any]]:
    return subjects_db


@app.get("/api/divisions")
async def get_divisions() -> list[dict[str, Any]]:
    return divisions_db


@app.get("/api/faculty")
async def get_faculty() -> list[dict[str, Any]]:
    return faculty_db


@app.get("/api/marks")
async def get_marks(
    subject_id: str | None = Query(None),
    student_id: str | None = Query(None),
) -> list[dict[str, Any]]:
    results = marks_db
    if subject_id:
        results = [m for m in results if m.get("subject_id") == subject_id]
    if student_id:
        results = [m for m in results if m.get("student_id") == student_id]
    return results


@app.post("/api/marks/publish")
async def publish_marks(body: PublishMarksRequest) -> dict[str, Any]:
    updated_count = 0
    now_iso = datetime.now(UTC).isoformat()
    for m in body.marks:
        existing = next(
            (item for item in marks_db if item["student_id"] == m.get("student_id") and item["subject_id"] == body.subject_id),
            None,
        )
        if existing:
            mark_history_db.append({
                "mark_id": existing["id"],
                "previous_score": existing["score"],
                "new_score": m.get("score"),
                "source": body.published_by,
                "timestamp": now_iso,
            })
            existing["score"] = m.get("score")
            existing["status"] = "published"
            existing["source"] = body.published_by
            existing["last_updated"] = now_iso
            updated_count += 1
        else:
            new_mark = {
                "id": f"mrk_{len(marks_db) + 1:03d}",
                "student_id": m.get("student_id"),
                "subject_id": body.subject_id,
                "score": m.get("score"),
                "max_score": m.get("max_score", 100.0),
                "status": "published",
                "source": body.published_by,
                "last_updated": now_iso,
            }
            marks_db.append(new_mark)
            updated_count += 1

    return {"status": "published", "subject_id": body.subject_id, "count": updated_count}


@app.put("/api/marks")
async def update_single_mark(payload: dict[str, Any]) -> dict[str, Any]:
    student_id = payload.get("student_id")
    subject_id = payload.get("subject_id")
    mark = next((m for m in marks_db if m["student_id"] == student_id and (not subject_id or m["subject_id"] == subject_id)), None)
    if not mark:
        raise HTTPException(status_code=404, detail="Mark record not found")
    mark.update(payload)
    mark["last_updated"] = datetime.now(UTC).isoformat()
    return mark


@app.get("/api/attendance")
async def get_attendance(division: str | None = Query(None)) -> list[dict[str, Any]]:
    return [
        {"student_id": s["id"], "name": s["name"], "attendance_pct": s["attendance_pct"]}
        for s in students_db
        if not division or s.get("division") == division
    ]


# ── Web UI ───────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def erp_ui() -> str:
    students_html = "".join(
        f"<tr><td>{s['roll_number']}</td><td><b>{s['name']}</b></td><td>{s['division']}</td><td>{s['attendance_pct']}%</td></tr>"
        for s in students_db
    )
    marks_html = "".join(
        f"<tr><td>{m.get('student_name', m['student_id'])}</td><td>{m.get('subject_code', m['subject_id'])}</td><td><b>{m['score']}</b>/{m['max_score']}</td><td><span class='badge'>{m['status']}</span></td><td>{m['source']}</td></tr>"
        for m in marks_db
    )
    return f"""<!DOCTYPE html>
<html>
<head>
  <title>Campus ERP — Standalone Mock</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 2rem; background: #FAF9F6; color: #1E2A32; }}
    h1 {{ color: #0E6B6B; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 2rem; background: #FFF; border: 1px solid #D9D2C2; }}
    th, td {{ padding: 8px 12px; text-align: left; border-bottom: 1px solid #E9E4D8; }}
    th {{ background: #F2EEE5; }}
    .badge {{ background: #D7ECE9; color: #0E6B6B; padding: 2px 8px; border-radius: 4px; font-size: 12px; }}
  </style>
</head>
<body>
  <h1>Campus ERP — Standalone Mock Service (:8101)</h1>
  <h2>Students Register</h2>
  <table>
    <tr><th>Roll No</th><th>Name</th><th>Division</th><th>Attendance</th></tr>
    {students_html}
  </table>
  <h2>Exam Marks Register</h2>
  <table>
    <tr><th>Student</th><th>Subject</th><th>Score</th><th>Status</th><th>Source</th></tr>
    {marks_html}
  </table>
</body>
</html>"""
