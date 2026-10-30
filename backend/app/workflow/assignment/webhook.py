"""Webhook Handler for assignment.submitted Events (EPIC-16-T02).

Validates HMAC-SHA256 signature, deduplicates via idempotency key,
and triggers the automated assignment evaluation workflow.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class WebhookProcessResult:
    is_valid: bool
    event_id: str
    run_id: str | None
    status: str  # "accepted", "duplicate_ignored", "signature_failed", "malformed"
    error: str | None = None
    payload: dict[str, Any] | None = None


class AssignmentWebhookHandler:
    """Processes incoming assignment webhook events from LMS."""

    def __init__(self, secret_key: str = "lms-webhook-secret-key-2026") -> None:
        self.secret_key = secret_key
        self._processed_event_ids: set[str] = set()

    def verify_signature(self, raw_payload: bytes, signature_header: str) -> bool:
        """Verify HMAC-SHA256 signature against secret key."""
        if not signature_header:
            return False

        expected_sig = hmac.new(
            self.secret_key.encode("utf-8"),
            raw_payload,
            hashlib.sha256,
        ).hexdigest()

        # Handle sha256= prefix if present
        provided_sig = signature_header.replace("sha256=", "").strip()
        return hmac.compare_digest(expected_sig, provided_sig)

    def process_webhook(
        self,
        raw_payload: bytes,
        signature: str,
        idempotency_key: str | None = None,
    ) -> WebhookProcessResult:
        """Process, verify, and route assignment webhook payload."""
        if not self.verify_signature(raw_payload, signature):
            return WebhookProcessResult(
                is_valid=False,
                event_id="",
                run_id=None,
                status="signature_failed",
                error="Invalid HMAC-SHA256 signature",
            )

        try:
            data = json.loads(raw_payload.decode("utf-8"))
        except Exception as e:
            return WebhookProcessResult(
                is_valid=False,
                event_id="",
                run_id=None,
                status="malformed",
                error=f"Malformed JSON: {e}",
            )

        event_id = idempotency_key or data.get("event_id") or f"evt_{hashlib.md5(raw_payload).hexdigest()[:12]}"

        # Idempotency check
        if event_id in self._processed_event_ids:
            return WebhookProcessResult(
                is_valid=True,
                event_id=event_id,
                run_id=None,
                status="duplicate_ignored",
                error="Event already processed",
                payload=data,
            )

        self._processed_event_ids.add(event_id)
        run_id = f"run_asgn_{event_id[:12]}"

        return WebhookProcessResult(
            is_valid=True,
            event_id=event_id,
            run_id=run_id,
            status="accepted",
            error=None,
            payload=data,
        )
