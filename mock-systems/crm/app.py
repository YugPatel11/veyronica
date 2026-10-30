"""CRM Mock Service (Port 8103).

EPIC-11-T03: Student CRM service (FastAPI + crm_db + Kanban UI).
Endpoints match backend/app/connectors/crm.py.
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
from shared.data import CONTACTS, PIPELINE, TICKETS

app = FastAPI(title="CRM Mock Service", version="0.1.0")
app.add_middleware(ChaosMiddleware)

contacts_db = copy.deepcopy(CONTACTS)
tickets_db = copy.deepcopy(TICKETS)
notes_db: list[dict[str, Any]] = []


class ChaosRequest(BaseModel):
    mode: str = "outage"
    duration_s: float = 30.0
    latency_ms: int = 2000
    error_rate: float = 0.5


class CreateNoteRequest(BaseModel):
    contact_id: str
    note: str
    author: str = "NEXUS Agent"


class CreateTicketRequest(BaseModel):
    contact_id: str
    title: str
    priority: str = "medium"  # low, medium, high, critical
    stage: str = "New"
    created_by: str = "NEXUS Agent"


class MoveStageRequest(BaseModel):
    ticket_id: str
    new_stage: str  # New, In Progress, Resolved


# ── Health & Admin ───────────────────────────────────────────────────────────

@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "crm", "timestamp": datetime.now(UTC).isoformat()}


@app.post("/_admin/chaos")
async def trigger_chaos(body: ChaosRequest) -> dict[str, Any]:
    return chaos_state.activate(body.mode, body.duration_s, latency_ms=body.latency_ms, error_rate=body.error_rate)


@app.post("/_admin/reset")
async def reset_state() -> dict[str, str]:
    global contacts_db, tickets_db, notes_db
    contacts_db = copy.deepcopy(CONTACTS)
    tickets_db = copy.deepcopy(TICKETS)
    notes_db = []
    chaos_state.reset()
    return {"status": "reset_complete"}


# ── CRM API Endpoints ────────────────────────────────────────────────────────

@app.get("/api/contacts")
async def get_contacts(stage: str | None = Query(None)) -> list[dict[str, Any]]:
    if stage:
        return [c for c in contacts_db if c.get("stage") == stage]
    return contacts_db


@app.get("/api/contacts/{contact_id}")
async def get_contact(contact_id: str) -> dict[str, Any]:
    c = next((item for item in contacts_db if item["id"] == contact_id or item.get("student_id") == contact_id), None)
    if not c:
        raise HTTPException(status_code=404, detail="Contact not found")
    return c


@app.put("/api/contacts/{contact_id}")
async def update_contact(contact_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    c = next((item for item in contacts_db if item["id"] == contact_id or item.get("student_id") == contact_id), None)
    if not c:
        raise HTTPException(status_code=404, detail="Contact not found")
    c.update(payload)
    return c


@app.post("/api/notes")
async def create_note(body: CreateNoteRequest) -> dict[str, Any]:
    note = {
        "id": f"not_{len(notes_db) + 1:03d}",
        "contact_id": body.contact_id,
        "note": body.note,
        "author": body.author,
        "created_at": datetime.now(UTC).isoformat(),
    }
    notes_db.append(note)
    return note


@app.get("/api/tickets")
async def get_tickets(stage: str | None = Query(None)) -> list[dict[str, Any]]:
    if stage:
        return [t for t in tickets_db if t.get("stage") == stage]
    return tickets_db


@app.post("/api/tickets")
async def create_ticket(body: CreateTicketRequest) -> dict[str, Any]:
    contact = next((c for c in contacts_db if c["id"] == body.contact_id), None)
    student_name = contact["name"] if contact else "Student"
    ticket = {
        "id": f"tkt_{len(tickets_db) + 1:03d}",
        "contact_id": body.contact_id,
        "student_name": student_name,
        "title": body.title,
        "priority": body.priority,
        "stage": body.stage,
        "created_by": body.created_by,
        "created_at": datetime.now(UTC).isoformat(),
    }
    tickets_db.append(ticket)
    return ticket


@app.patch("/api/tickets/{ticket_id}")
async def update_ticket(ticket_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    t = next((item for item in tickets_db if item["id"] == ticket_id), None)
    if not t:
        raise HTTPException(status_code=404, detail="Ticket not found")
    t.update(payload)
    return t


@app.get("/api/pipeline")
async def get_pipeline() -> list[dict[str, Any]]:
    return [
        {"stage": "New", "tickets": [t for t in tickets_db if t.get("stage") == "New"]},
        {"stage": "In Progress", "tickets": [t for t in tickets_db if t.get("stage") == "In Progress"]},
        {"stage": "Resolved", "tickets": [t for t in tickets_db if t.get("stage") == "Resolved"]},
    ]


@app.post("/api/pipeline/move")
async def move_pipeline_stage(body: MoveStageRequest) -> dict[str, Any]:
    t = next((item for item in tickets_db if item["id"] == body.ticket_id), None)
    if not t:
        raise HTTPException(status_code=404, detail="Ticket not found")
    t["stage"] = body.new_stage
    t["last_moved"] = datetime.now(UTC).isoformat()
    return {"status": "moved", "ticket_id": body.ticket_id, "new_stage": body.new_stage}


# ── Web UI: Kanban Board ─────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def crm_kanban_ui() -> str:
    new_cards = "".join(
        f"<div class='card'><b>{t['title']}</b><br><small>{t['student_name']} • {t['priority'].upper()}</small></div>"
        for t in tickets_db if t.get("stage") == "New"
    )
    in_prog_cards = "".join(
        f"<div class='card'><b>{t['title']}</b><br><small>{t['student_name']} • {t['priority'].upper()}</small></div>"
        for t in tickets_db if t.get("stage") == "In Progress"
    )
    res_cards = "".join(
        f"<div class='card'><b>{t['title']}</b><br><small>{t['student_name']} • {t['priority'].upper()}</small></div>"
        for t in tickets_db if t.get("stage") == "Resolved"
    )
    return f"""<!DOCTYPE html>
<html>
<head>
  <title>Student CRM — Kanban Board Mock</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 2rem; background: #FAF9F6; color: #1E2A32; }}
    h1 {{ color: #C47D1B; }}
    .kanban {{ display: flex; gap: 1.5rem; }}
    .column {{ flex: 1; background: #F2EEE5; border: 1px solid #D9D2C2; border-radius: 8px; padding: 1rem; min-height: 300px; }}
    .card {{ background: #FFF; border: 1px solid #D9D2C2; border-radius: 6px; padding: 0.75rem; margin-bottom: 0.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
    .column h3 {{ margin-top: 0; color: #364650; }}
  </style>
</head>
<body>
  <h1>Student Counselling CRM — Standalone Mock (:8103)</h1>
  <div class="kanban">
    <div class="column">
      <h3>New ({len([t for t in tickets_db if t.get('stage') == 'New'])})</h3>
      {new_cards or '<p><i>No new tickets</i></p>'}
    </div>
    <div class="column">
      <h3>In Progress ({len([t for t in tickets_db if t.get('stage') == 'In Progress'])})</h3>
      {in_prog_cards or '<p><i>No tickets in progress</i></p>'}
    </div>
    <div class="column">
      <h3>Resolved ({len([t for t in tickets_db if t.get('stage') == 'Resolved'])})</h3>
      {res_cards or '<p><i>No resolved tickets</i></p>'}
    </div>
  </div>
</body>
</html>"""
