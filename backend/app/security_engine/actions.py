"""Automated security response actions.

EPIC-18-T06: Automated temporary responses (lockout, IP block, session revocation).
Manages temporary or permanent blocks and active entity containment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any
import uuid

import structlog

from app.core.token_blacklist import blacklist_token

logger = structlog.get_logger()


@dataclass
class BlockRecord:
    """Record of an active block or lockout."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: str = "ip"  # ip or user
    entity_value: str = ""
    reason: str = ""
    blocked_by: str = "system"  # system or admin user_id
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    is_permanent: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_active(self) -> bool:
        """Check if block is currently active."""
        if self.is_permanent:
            return True
        if self.expires_at is None:
            return False
        return datetime.now(UTC) < self.expires_at


class SecurityActionHandler:
    """EPIC-18-T06: Executes automated security containment actions."""

    def __init__(self) -> None:
        # In-memory store for fast lookups; can also sync to BlockedEntity DB model
        self._blocks: dict[str, BlockRecord] = {}

    def _block_key(self, entity_type: str, entity_value: str) -> str:
        return f"{entity_type.lower()}:{entity_value.strip().lower()}"

    def lock_account(
        self,
        user_id_or_email: str,
        reason: str,
        duration_minutes: int = 30,
        blocked_by: str = "security_agent",
        metadata: dict[str, Any] | None = None,
    ) -> BlockRecord:
        """Lock a user account temporarily."""
        expires_at = datetime.now(UTC) + timedelta(minutes=duration_minutes)
        record = BlockRecord(
            entity_type="user",
            entity_value=user_id_or_email,
            reason=reason,
            blocked_by=blocked_by,
            expires_at=expires_at,
            is_permanent=False,
            metadata=metadata or {},
        )
        key = self._block_key("user", user_id_or_email)
        self._blocks[key] = record
        logger.warning(
            "security_account_locked",
            user=user_id_or_email,
            reason=reason,
            duration_minutes=duration_minutes,
            expires_at=expires_at.isoformat(),
        )
        return record

    def block_ip(
        self,
        ip_address: str,
        reason: str,
        duration_minutes: int = 60,
        is_permanent: bool = False,
        blocked_by: str = "security_agent",
        metadata: dict[str, Any] | None = None,
    ) -> BlockRecord:
        """Block an IP address temporarily or permanently."""
        expires_at = None if is_permanent else datetime.now(UTC) + timedelta(minutes=duration_minutes)
        record = BlockRecord(
            entity_type="ip",
            entity_value=ip_address,
            reason=reason,
            blocked_by=blocked_by,
            expires_at=expires_at,
            is_permanent=is_permanent,
            metadata=metadata or {},
        )
        key = self._block_key("ip", ip_address)
        self._blocks[key] = record
        logger.warning(
            "security_ip_blocked",
            ip=ip_address,
            reason=reason,
            duration_minutes=duration_minutes if not is_permanent else "permanent",
        )
        return record

    async def revoke_user_sessions(self, jt_list: list[str], exp_time: datetime | None = None) -> int:
        """Revoke active JWT tokens using the Redis blacklist."""
        expiry = exp_time or (datetime.now(UTC) + timedelta(hours=24))
        revoked_count = 0
        for jti in jt_list:
            try:
                await blacklist_token(jti, expiry)
                revoked_count += 1
            except Exception as e:
                logger.error("session_revocation_failed", jti=jti, error=str(e))
        return revoked_count

    def is_blocked(self, entity_type: str, entity_value: str) -> bool:
        """Check whether an IP or user is currently blocked."""
        key = self._block_key(entity_type, entity_value)
        record = self._blocks.get(key)
        if not record:
            return False
        if record.is_active:
            return True
        # Expired block: clean up
        del self._blocks[key]
        return False

    def unblock(self, entity_type: str, entity_value: str) -> bool:
        """Manually release a block on an IP or user."""
        key = self._block_key(entity_type, entity_value)
        if key in self._blocks:
            del self._blocks[key]
            logger.info("security_entity_unblocked", entity_type=entity_type, entity_value=entity_value)
            return True
        return False

    def list_active_blocks(self) -> list[BlockRecord]:
        """List all currently active blocks."""
        now = datetime.now(UTC)
        active: list[BlockRecord] = []
        expired_keys: list[str] = []

        for key, rec in self._blocks.items():
            if rec.is_active:
                active.append(rec)
            else:
                expired_keys.append(key)

        for key in expired_keys:
            del self._blocks[key]

        return active


# Global handler instance
action_handler = SecurityActionHandler()
