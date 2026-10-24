"""Event Streaming & SSE API endpoints.

EPIC-10: Event streaming with SSE.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.events import NexusEvent, emitter, sse_stream

router = APIRouter(prefix="/events", tags=["Events"])


# ── Request Models ───────────────────────────────────────────────────────────

class EmitEventRequest(BaseModel):
    type: str  # run_started, step_completed, approval_needed, status_change, agent_action, error
    run_id: str | None = None
    task_id: str | None = None
    agent_id: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/stream")
async def event_stream(run_id: str | None = Query(None)) -> StreamingResponse:
    """EPIC-10-T02: SSE endpoint for real-time events.

    Optionally filter by run_id. Sends keepalive comments every 30s.
    """
    queue = emitter.subscribe()

    async def generate():
        try:
            async for chunk in sse_stream(queue, run_id=run_id):
                yield chunk
        finally:
            emitter.unsubscribe(queue)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/emit")
async def emit_event(body: EmitEventRequest) -> dict[str, str]:
    """Emit a new event to all subscribers."""
    event = NexusEvent(**body.model_dump())
    await emitter.emit(event)
    return {"event_id": event.id, "status": "emitted"}


@router.get("/history")
async def event_history(
    run_id: str | None = Query(None),
    event_type: str | None = Query(None),
    limit: int = Query(50, le=200),
) -> list[dict[str, Any]]:
    """EPIC-10-T03: Get recent event history with optional filters."""
    events = emitter.get_history(run_id=run_id, event_type=event_type, limit=limit)
    return [e.model_dump(mode="json") for e in events]
