"""Security ORM models.

EPIC-03-T08: security_events, blocked_entities, login_attempts.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.mixins import TimestampMixin, generate_uuid
from app.db.session import Base


class SecurityEvent(Base):
    """Security event log entry."""

    __tablename__ = "security_events"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    event_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # failed_login, unusual_login, suspicious_op, rate_limit_hit, ip_blocked
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # info, warning, critical
    source_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    resolved: Mapped[bool] = mapped_column(default=False, nullable=False)
    resolved_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_security_events_type", "event_type"),
        Index("ix_security_events_severity", "severity"),
        Index("ix_security_events_created_at", "created_at"),
        Index("ix_security_events_source_ip", "source_ip"),
    )


class BlockedEntity(TimestampMixin, Base):
    """Temporarily or permanently blocked entity (IP, user)."""

    __tablename__ = "blocked_entities"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    entity_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # ip, user
    entity_value: Mapped[str] = mapped_column(String(255), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    blocked_by: Mapped[str | None] = mapped_column(String(36), nullable=True)  # user_id or "system"
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_permanent: Mapped[bool] = mapped_column(default=False, nullable=False)

    __table_args__ = (
        Index("ix_blocked_entities_type_value", "entity_type", "entity_value"),
        Index("ix_blocked_entities_expires", "expires_at"),
    )


class LoginAttempt(Base):
    """Login attempt record for brute-force detection."""

    __tablename__ = "login_attempts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source_ip: Mapped[str] = mapped_column(String(45), nullable=False)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    success: Mapped[bool] = mapped_column(nullable=False)
    failure_reason: Mapped[str | None] = mapped_column(String(100), nullable=True)
    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_login_attempts_email_time", "email", "attempted_at"),
        Index("ix_login_attempts_ip_time", "source_ip", "attempted_at"),
    )
