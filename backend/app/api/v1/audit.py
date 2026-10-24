"""Decision Ledger API endpoints.

EPIC-09: Hash-chained audit trail.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.audit import ledger, LedgerEntry

router = APIRouter(prefix="/audit", tags=["Audit"])


# ── Request Models ───────────────────────────────────────────────────────────

class AppendLedgerRequest(BaseModel):
    event_type: str  # decision, action, approval, connector_call, error
    action: str
    run_id: str | None = None
    task_id: str | None = None
    agent_id: str | None = None
    user_id: str | None = None
    entity_type: str | None = None
    entity_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    reasoning: str | None = None
    confidence: float | None = None
    model_used: str | None = None
    tokens_used: int | None = None


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/")
async def query_ledger(
    run_id: str | None = Query(None),
    event_type: str | None = Query(None),
    agent_id: str | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """EPIC-09-T04: Query ledger entries with filters and pagination."""
    entries = ledger.query(
        run_id=run_id,
        event_type=event_type,
        agent_id=agent_id,
        limit=limit,
        offset=offset,
    )
    return {
        "entries": [e.model_dump(mode="json") for e in entries],
        "total": ledger.count,
        "limit": limit,
        "offset": offset,
    }


@router.post("/")
async def append_entry(body: AppendLedgerRequest) -> dict[str, Any]:
    """Append a new entry to the decision ledger."""
    entry = ledger.append(**body.model_dump())
    return entry.model_dump(mode="json")


@router.get("/verify")
async def verify_chain() -> dict[str, Any]:
    """EPIC-09-T02: Verify the integrity of the hash chain.

    Returns whether the chain is valid and the last verified sequence number.
    """
    is_valid, last_seq = ledger.verify_chain()
    return {
        "valid": is_valid,
        "last_verified_sequence": last_seq,
        "total_entries": ledger.count,
    }


@router.get("/stats")
async def ledger_stats() -> dict[str, Any]:
    """Get ledger statistics."""
    return {
        "total_entries": ledger.count,
        "chain_verified": ledger.verify_chain()[0],
    }
