"""Data Retention Policies and Cleanup Engine.

EPIC-24-T05: Data retention policies and automated cleanup jobs.
Enforces statutory campus retention windows while preserving immutable audit logs.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any


class RetentionPolicy:
    """Retention rule definition."""

    def __init__(
        self,
        entity: str,
        retention_days: int | None,  # None means immutable / keep forever
        description: str,
    ) -> None:
        self.entity = entity
        self.retention_days = retention_days
        self.description = description

    def is_eligible_for_purge(self, created_at: datetime) -> bool:
        """Return True if record is past its retention threshold."""
        if self.retention_days is None:
            return False  # Immutable
        cutoff = datetime.now(UTC) - timedelta(days=self.retention_days)
        # Ensure timezone-aware comparison
        ts = created_at if created_at.tzinfo else created_at.replace(tzinfo=UTC)
        return ts < cutoff


DEFAULT_POLICIES: dict[str, RetentionPolicy] = {
    "audit_ledger": RetentionPolicy("audit_ledger", None, "Immutable cryptographic ledger (never purged)"),
    "workflow_checkpoints": RetentionPolicy("workflow_checkpoints", 90, "Retain execution checkpoints for 90 days"),
    "ephemeral_uploads": RetentionPolicy("ephemeral_uploads", 14, "Retain raw OCR temporary files for 14 days"),
    "login_attempts": RetentionPolicy("login_attempts", 7, "Retain security access logs for 7 days"),
}


class RetentionManager:
    """Manages retention evaluation and automated cleanup tasks."""

    def __init__(self, policies: dict[str, RetentionPolicy] | None = None) -> None:
        self.policies = policies or DEFAULT_POLICIES

    def evaluate_item(self, entity_type: str, created_at: datetime) -> bool:
        """Check if an item of entity_type should be purged."""
        policy = self.policies.get(entity_type)
        if not policy:
            return False
        return policy.is_eligible_for_purge(created_at)

    def run_cleanup_job(self) -> dict[str, int]:
        """Execute simulated cleanup across retention policies."""
        return {
            "purged_checkpoints": 0,
            "purged_ephemeral_uploads": 0,
            "purged_login_attempts": 0,
            "purged_audit_entries": 0,  # Always 0 (immutable)
        }


retention_manager = RetentionManager()
