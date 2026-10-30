"""Notification Service.

EPIC-21-T01: Multi-channel routing (in-app, email, telegram).
EPIC-21-T02: Email templates.
EPIC-21-T04: Notification preferences.
EPIC-21-T05: Delivery status tracking.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger()


class NotificationChannel:
    IN_APP = "in_app"
    EMAIL = "email"
    TELEGRAM = "telegram"


class NotificationCategory:
    APPROVAL = "approval"
    WORKFLOW = "workflow"
    SECURITY = "security"
    BUDGET = "budget"
    SYSTEM = "system"


class NotificationData(BaseModel):
    """Notification payload."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    channel: str
    category: str
    title: str
    body: str = ""
    link: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    delivery_status: str = "pending"  # pending, sent, delivered, failed
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ── User Preferences ─────────────────────────────────────────────────────────

DEFAULT_PREFERENCES: dict[str, list[str]] = {
    NotificationCategory.APPROVAL: [NotificationChannel.IN_APP, NotificationChannel.EMAIL],
    NotificationCategory.WORKFLOW: [NotificationChannel.IN_APP],
    NotificationCategory.SECURITY: [NotificationChannel.IN_APP, NotificationChannel.EMAIL],
    NotificationCategory.BUDGET: [NotificationChannel.IN_APP],
    NotificationCategory.SYSTEM: [NotificationChannel.IN_APP],
}


class NotificationDispatcher:
    """EPIC-21-T01: Multi-channel notification dispatcher."""

    def __init__(self) -> None:
        self._notifications: list[NotificationData] = []
        self._preferences: dict[str, dict[str, list[str]]] = {}

    def set_preferences(
        self,
        user_id: str,
        preferences: dict[str, list[str]] | None = None,
        *,
        prefs: dict[str, list[str]] | None = None,
    ) -> None:
        """EPIC-21-T04: Set user notification preferences."""
        self._preferences[user_id] = preferences or prefs or {}

    def get_channels(self, user_id: str, category: str) -> list[str]:
        """Get preferred channels for a user and category."""
        user_prefs = self._preferences.get(user_id, DEFAULT_PREFERENCES)
        return user_prefs.get(category, [NotificationChannel.IN_APP])

    async def send(
        self,
        user_id: str,
        category: str,
        title: str,
        body: str = "",
        *,
        link: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> list[NotificationData]:
        """Send notification through all preferred channels."""
        channels = self.get_channels(user_id, category)
        results = []

        for channel in channels:
            notif = NotificationData(
                user_id=user_id,
                channel=channel,
                category=category,
                title=title,
                body=body,
                link=link,
                payload=payload or {},
            )

            try:
                await self._deliver(notif)
                notif.delivery_status = "sent"
            except Exception as e:
                notif.delivery_status = "failed"
                logger.error("notification_delivery_failed", channel=channel, error=str(e))

            self._notifications.append(notif)
            results.append(notif)

        return results

    async def _deliver(self, notif: NotificationData) -> None:
        """Deliver a notification through its channel."""
        if notif.channel == NotificationChannel.IN_APP:
            logger.info("notification_in_app", user=notif.user_id, title=notif.title)
        elif notif.channel == NotificationChannel.EMAIL:
            logger.info("notification_email", user=notif.user_id, title=notif.title)
            # In production: use EmailConnector
        elif notif.channel == NotificationChannel.TELEGRAM:
            logger.info("notification_telegram", user=notif.user_id, title=notif.title)
            # In production: use TelegramConnector

    def get_unread(self, user_id: str) -> list[NotificationData]:
        """Get unread in-app notifications for a user."""
        return [
            n for n in self._notifications
            if n.user_id == user_id
            and n.channel == NotificationChannel.IN_APP
            and n.delivery_status != "read"
        ]


# ── Email Templates ──────────────────────────────────────────────────────────

EMAIL_TEMPLATES: dict[str, str] = {
    "approval_needed": """
<h2>Approval Required: {title}</h2>
<p>{description}</p>
<p><strong>Risk Level:</strong> {risk_level}</p>
<p><strong>Expires:</strong> {expires_at}</p>
<p><a href="{link}">Review and Approve</a></p>
""",
    "marks_published": """
<h2>Marks Published: {subject}</h2>
<p>Marks for {subject} ({division}) have been published.</p>
<p><strong>Students:</strong> {student_count}</p>
<p><strong>Average:</strong> {average_marks}</p>
""",
    "security_alert": """
<h2>Security Alert: {event_type}</h2>
<p>{description}</p>
<p><strong>Severity:</strong> {severity}</p>
<p><strong>Source IP:</strong> {source_ip}</p>
""",
    "budget_warning": """
<h2>Budget Alert: {scope} Token Budget</h2>
<p>Usage has reached {percentage}% of the {period} limit.</p>
<p><strong>Used:</strong> {used} / {limit} tokens</p>
""",
}


# Singleton
dispatcher = NotificationDispatcher()
