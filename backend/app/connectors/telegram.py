"""Telegram Connector Adapter. EPIC-05-T11."""
from __future__ import annotations
from typing import Any
import httpx, structlog
from app.connectors import BaseConnector, ConnectorResult, ConnectorStatus

logger = structlog.get_logger()

class TelegramConnector(BaseConnector):
    """Telegram Bot API connector for notifications and approval callbacks."""

    async def execute(self, operation: str, payload: dict[str, Any] | None = None, *, dry_run: bool = False, idempotency_key: str | None = None) -> ConnectorResult:
        payload = payload or {}
        bot_token = self.auth_config.get("bot_token", "")
        if operation == "send_message":
            if dry_run:
                return ConnectorResult(success=True, data=payload, is_dry_run=True)
            chat_id = payload.get("chat_id")
            text = payload.get("text", "")
            reply_markup = payload.get("reply_markup")
            body: dict[str, Any] = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
            if reply_markup:
                body["reply_markup"] = reply_markup
            try:
                async with httpx.AsyncClient(timeout=15) as client:
                    resp = await client.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json=body)
                    data = resp.json()
                return ConnectorResult(success=data.get("ok", False), data=data, status_code=resp.status_code)
            except Exception as e:
                return ConnectorResult(success=False, error=str(e))
        return ConnectorResult(success=False, error=f"Unknown telegram operation: {operation}")

    async def health_check(self) -> ConnectorStatus:
        bot_token = self.auth_config.get("bot_token", "")
        if not bot_token:
            return ConnectorStatus.UNKNOWN
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"https://api.telegram.org/bot{bot_token}/getMe")
                return ConnectorStatus.HEALTHY if resp.status_code == 200 else ConnectorStatus.DOWN
        except Exception:
            return ConnectorStatus.DOWN
