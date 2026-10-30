"""Outbound Webhook Request Signing.

EPIC-24-T04: Webhook request signing (outbound) with HMAC-SHA256 and replay protection.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any


def sign_webhook_payload(
    secret: str,
    payload: dict[str, Any] | str,
    timestamp: int | None = None,
) -> tuple[str, str]:
    """Generate HMAC-SHA256 signature and timestamp for an outbound webhook payload.

    Returns:
        (signature_hex, timestamp_str)
    """
    ts = str(timestamp or int(time.time()))
    raw_payload = payload if isinstance(payload, str) else json.dumps(payload, sort_keys=True)
    message = f"t={ts}.v1={raw_payload}".encode("utf-8")
    sig = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()
    return sig, ts


def verify_webhook_signature(
    secret: str,
    payload: dict[str, Any] | str,
    signature: str,
    timestamp_str: str,
    max_drift_seconds: int = 300,
) -> bool:
    """Verify an inbound or outbound webhook signature against replay attacks."""
    try:
        ts = int(timestamp_str)
    except (ValueError, TypeError):
        return False

    # Check clock drift / replay window
    now = int(time.time())
    if abs(now - ts) > max_drift_seconds:
        return False

    expected_sig, _ = sign_webhook_payload(secret, payload, timestamp=ts)
    return hmac.compare_digest(expected_sig, signature)
