"""Unit tests for Events Streaming (SSE) and Notification Service.

EPIC-10: Event emitter, filtering, and SSE.
EPIC-21: Multi-channel notifications, preferences, and delivery tracking.
"""

from __future__ import annotations

import asyncio
import json

import pytest

from app.events import EventEmitter, NexusEvent, sse_stream
from app.notifications import (
    NotificationCategory,
    NotificationChannel,
    NotificationDispatcher,
)


class TestEventEmitter:
    @pytest.mark.asyncio
    async def test_subscribes_and_receives_event(self) -> None:
        emitter = EventEmitter()
        queue = emitter.subscribe()

        event = NexusEvent(
            type="step_completed",
            run_id="run_101",
            data={"step": "evaluate", "score": 85},
        )
        await emitter.emit(event)

        received = await queue.get()
        assert received.type == "step_completed"
        assert received.run_id == "run_101"
        assert received.data["score"] == 85

        emitter.unsubscribe(queue)

    @pytest.mark.asyncio
    async def test_sse_stream_format(self) -> None:
        queue: asyncio.Queue[NexusEvent] = asyncio.Queue()
        event = NexusEvent(
            type="workflow_started",
            run_id="run_102",
            data={"name": "Exam Processing"},
        )
        queue.put_nowait(event)

        # Read first chunk from generator
        stream = sse_stream(queue)
        chunk = await anext(stream)
        assert "event: workflow_started" in chunk
        assert "data: " in chunk
        assert chunk.endswith("\n\n")

        for line in chunk.split("\n"):
            if line.startswith("data: "):
                payload = json.loads(line[len("data: "):])
                assert payload["type"] == "workflow_started"
                assert payload["run_id"] == "run_102"
                break


class TestNotificationService:
    @pytest.mark.asyncio
    async def test_dispatches_to_preferred_channels(self) -> None:
        dispatcher = NotificationDispatcher()
        notifs = await dispatcher.send(
            user_id="usr_admin_001",
            category=NotificationCategory.APPROVAL,
            title="Approval required for CS301 marks",
            body="Review 47 student marks before publishing to ERP.",
        )

        # Default preferences for APPROVAL: in_app and email
        channels = [n.channel for n in notifs]
        assert NotificationChannel.IN_APP in channels
        assert NotificationChannel.EMAIL in channels

    @pytest.mark.asyncio
    async def test_respects_custom_user_preferences(self) -> None:
        dispatcher = NotificationDispatcher()
        dispatcher.set_preferences(
            user_id="usr_approver_001",
            preferences={NotificationCategory.APPROVAL: [NotificationChannel.TELEGRAM]},
        )

        notifs = await dispatcher.send(
            user_id="usr_approver_001",
            category=NotificationCategory.APPROVAL,
            title="Telegram Alert",
        )
        assert len(notifs) == 1
        assert notifs[0].channel == NotificationChannel.TELEGRAM
