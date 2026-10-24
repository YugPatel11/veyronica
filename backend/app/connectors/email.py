"""Email Connector Adapter (SMTP). EPIC-05-T10."""
from __future__ import annotations
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any
import structlog
from app.connectors import BaseConnector, ConnectorResult, ConnectorStatus

logger = structlog.get_logger()

class EmailConnector(BaseConnector):
    """Email connector via SMTP (Mailpit in dev)."""

    async def execute(self, operation: str, payload: dict[str, Any] | None = None, *, dry_run: bool = False, idempotency_key: str | None = None) -> ConnectorResult:
        payload = payload or {}
        if operation != "send_email":
            return ConnectorResult(success=False, error=f"Unknown email operation: {operation}")

        to = payload.get("to", "")
        subject = payload.get("subject", "")
        body = payload.get("body", "")
        html = payload.get("html")

        if dry_run:
            return ConnectorResult(success=True, data={"to": to, "subject": subject, "preview": body[:200]}, is_dry_run=True, idempotency_key=idempotency_key)

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = payload.get("from", "nexus@campus.edu")
            msg["To"] = to
            msg.attach(MIMEText(body, "plain"))
            if html:
                msg.attach(MIMEText(html, "html"))

            # Parse host:port from base_url
            host = self.base_url.replace("http://", "").replace("https://", "")
            smtp_host, _, smtp_port = host.partition(":")
            port = int(smtp_port) if smtp_port else 1025

            with smtplib.SMTP(smtp_host, port, timeout=10) as server:
                server.send_message(msg)

            return ConnectorResult(success=True, data={"message_id": msg["Message-ID"]}, idempotency_key=idempotency_key)
        except Exception as e:
            logger.error("email_send_failed", error=str(e))
            return ConnectorResult(success=False, error=str(e))

    async def health_check(self) -> ConnectorStatus:
        try:
            host = self.base_url.replace("http://", "").replace("https://", "")
            smtp_host, _, smtp_port = host.partition(":")
            port = int(smtp_port) if smtp_port else 1025
            with smtplib.SMTP(smtp_host, port, timeout=5) as server:
                server.noop()
            return ConnectorStatus.HEALTHY
        except Exception:
            return ConnectorStatus.DOWN
