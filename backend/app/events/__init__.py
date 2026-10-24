"""Event Streaming & SSE.

EPIC-10-T01: Event emitter (Redis pub/sub).
EPIC-10-T02: SSE endpoint.
EPIC-10-T05: Event schema.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from datetime import UTC, datetime
from typing import Any, AsyncGenerator

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger()


# ── Event Schema ─────────────────────────────────────────────────────────────

class NexusEvent(BaseModel):
    """EPIC-10-T05: Typed event schema."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str  # run_started, step_completed, approval_needed, status_change, agent_action, error
    run_id: str | None = None
    task_id: str | None = None
    agent_id: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ── Event Emitter ────────────────────────────────────────────────────────────

_CHANNEL = "nexus:events"


class EventEmitter:
    """EPIC-10-T01: Event emitter backed by in-memory queue (Redis in production).

    In production, this would publish to Redis pub/sub.
    For local dev without Redis, uses asyncio Queue.
    """

    def __init__(self) -> None:
        self._subscribers: list[asyncio.Queue[NexusEvent]] = []
        self._history: list[NexusEvent] = []

    async def emit(self, event: NexusEvent) -> None:
        """Publish an event to all subscribers."""
        self._history.append(event)
        logger.info("event_emitted", type=event.type, run_id=event.run_id)

        for queue in self._subscribers:
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                pass  # Drop if subscriber is slow

    def subscribe(self) -> asyncio.Queue[NexusEvent]:
        """Create a new subscription queue."""
        queue: asyncio.Queue[NexusEvent] = asyncio.Queue(maxsize=100)
        self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[NexusEvent]) -> None:
        """Remove a subscription."""
        self._subscribers = [q for q in self._subscribers if q is not queue]

    def get_history(
        self, *, run_id: str | None = None, event_type: str | None = None, limit: int = 50
    ) -> list[NexusEvent]:
        """Get recent event history with optional filters. EPIC-10-T03."""
        filtered = self._history
        if run_id:
            filtered = [e for e in filtered if e.run_id == run_id]
        if event_type:
            filtered = [e for e in filtered if e.type == event_type]
        return filtered[-limit:]


# Singleton
emitter = EventEmitter()


# ── SSE Helpers ──────────────────────────────────────────────────────────────

def format_sse(event: NexusEvent) -> str:
    """Format an event as SSE data. EPIC-10-T02."""
    data = event.model_dump_json()
    return f"event: {event.type}\ndata: {data}\nid: {event.id}\n\n"


async def sse_stream(
    queue: asyncio.Queue[NexusEvent],
    *,
    run_id: str | None = None,
) -> AsyncGenerator[str, None]:
    """EPIC-10-T02/T03: Generate SSE stream with optional run_id filter."""
    while True:
        try:
            event = await asyncio.wait_for(queue.get(), timeout=30)
            # EPIC-10-T03: Filter by run_id if specified
            if run_id and event.run_id != run_id:
                continue
            yield format_sse(event)
        except asyncio.TimeoutError:
            # Send keepalive comment
            yield ": keepalive\n\n"
