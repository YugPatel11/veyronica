"""Outbound webhook dispatcher with HMAC SHA-256 signing.

EPIC-11-T04: Outbound webhooks (ERP: marks.updated, LMS: assignment.submitted).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any

import httpx
import structlog

logger = structlog.get_logger()

DEFAULT_SECRET = "nexus_webhook_secret_key_2026"


def compute_signature(payload_bytes: bytes, secret: str = DEFAULT_SECRET) -> str:
    """Compute HMAC-SHA256 signature for payload."""
    return hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()


async def emit_webhook(
    target_url: str,
    event_type: str,
    data: dict[str, Any],
    secret: str = DEFAULT_SECRET,
) -> bool:
    """Send signed webhook to target URL."""
    payload = {
        "event": event_type,
        "timestamp": int(time.time()),
        "data": data,
    }
    payload_bytes = json.dumps(payload, default=str).encode()
    signature = compute_signature(payload_bytes, secret)

    headers = {
        "Content-Type": "application/json",
        "X-Nexus-Signature": signature,
        "X-Nexus-Event": event_type,
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(target_url, content=payload_bytes, headers=headers)
            return resp.status_code in (200, 201, 202, 204)
    except Exception as e:
        logger.warning("webhook_delivery_failed", url=target_url, event=event_type, error=str(e))
        return False
