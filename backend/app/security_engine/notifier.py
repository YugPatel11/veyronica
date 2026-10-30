"""Admin security notification service.

EPIC-18-T07: Admin notification (email + Telegram + dashboard).
Routes urgent security incidents and containment actions to system administrators.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import structlog

from app.notifications import (
    NotificationCategory,
    NotificationChannel,
    NotificationData,
    dispatcher,
)
from app.security_engine.failed_logins import SecurityAlert

logger = structlog.get_logger()


@dataclass
class IncidentNotification:
    """Delivered admin notification record."""
    alert_id: str
    admin_id: str
    channel: str
    title: str
    content: str
    severity: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


class SecurityNotifier:
    """EPIC-18-T07: Dispatches security alerts across Email, Telegram, and Dashboard."""

    def __init__(self, admin_user_ids: list[str] | None = None) -> None:
        self.admin_user_ids = admin_user_ids or ["admin", "security_officer"]
        self.notification_log: list[IncidentNotification] = []

    def format_email_body(self, alert: SecurityAlert, action_taken: str | None = None) -> str:
        """Format an HTML security alert email."""
        action_html = f"<p><strong>Automated Action:</strong> {action_taken}</p>" if action_taken else ""
        return f"""
        <div style="font-family: sans-serif; max-width: 600px; padding: 16px; border-left: 4px solid #ef4444; background: #0f172a; color: #f8fafc;">
            <h2 style="color: #ef4444; margin-top: 0;">Security Alert: {alert.title}</h2>
            <p><strong>Severity:</strong> <span style="text-transform: uppercase; color: #f87171;">{alert.severity}</span></p>
            <p><strong>Rule:</strong> {alert.rule_name}</p>
            <p><strong>Description:</strong> {alert.description}</p>
            <p><strong>Target:</strong> {alert.target_type}: {alert.target_value}</p>
            <p><strong>Source IP:</strong> {alert.source_ip or 'N/A'}</p>
            <p><strong>Detected At:</strong> {alert.detected_at.isoformat()}</p>
            {action_html}
            <p style="margin-top: 20px;"><a href="/security" style="color: #38bdf8; text-decoration: underline;">Open Security Mission Control</a></p>
        </div>
        """

    def format_telegram_message(self, alert: SecurityAlert, action_taken: str | None = None) -> str:
        """Format Markdown for Telegram security alert."""
        icon = "🚨 CRITICAL" if alert.severity == "critical" else "⚠️ WARNING"
        lines = [
            f"*{icon} SECURITY ALERT*",
            f"*Title:* {alert.title}",
            f"*Severity:* `{alert.severity.upper()}`",
            f"*Rule:* `{alert.rule_name}`",
            f"*Target:* {alert.target_type} ({alert.target_value})",
        ]
        if alert.source_ip:
            lines.append(f"*Source IP:* `{alert.source_ip}`")
        if action_taken:
            lines.append(f"*Action Taken:* `{action_taken}`")
        lines.append(f"\n[View Dashboard](/security)")
        return "\n".join(lines)

    async def notify_admins(
        self,
        alert: SecurityAlert,
        action_taken: str | None = None,
    ) -> list[NotificationData]:
        """Send notifications to all configured admin channels."""
        dispatched_records: list[NotificationData] = []
        email_body = self.format_email_body(alert, action_taken)
        telegram_body = self.format_telegram_message(alert, action_taken)

        for admin_id in self.admin_user_ids:
            # Send through multi-channel dispatcher (Email, In-App, Telegram)
            records = await dispatcher.send(
                user_id=admin_id,
                category=NotificationCategory.SECURITY,
                title=f"[{alert.severity.upper()}] {alert.title}",
                body=email_body,
                link="/security",
                payload={
                    "alert_id": alert.id,
                    "rule": alert.rule_name,
                    "severity": alert.severity,
                    "target": alert.target_value,
                    "source_ip": alert.source_ip,
                    "action_taken": action_taken,
                    "telegram_text": telegram_body,
                },
            )

            for rec in records:
                self.notification_log.append(
                    IncidentNotification(
                        alert_id=alert.id,
                        admin_id=admin_id,
                        channel=rec.channel,
                        title=rec.title,
                        content=rec.body,
                        severity=alert.severity,
                    )
                )

            dispatched_records.extend(records)

        logger.info(
            "security_admins_notified",
            alert_id=alert.id,
            admins=self.admin_user_ids,
            dispatched_count=len(dispatched_records),
        )
        return dispatched_records


# Global notifier instance
security_notifier = SecurityNotifier()
