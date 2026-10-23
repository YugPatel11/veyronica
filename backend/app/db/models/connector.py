"""Connector ORM models.

EPIC-03-T06: connectors, connector_calls.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.mixins import TimestampMixin, generate_uuid
from app.db.session import Base


class Connector(TimestampMixin, Base):
    """Registered external system connector."""

    __tablename__ = "connectors"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    connector_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # erp, lms, crm, email, telegram, storage
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    auth_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    health_status: Mapped[str] = mapped_column(
        String(20), default="unknown", nullable=False
    )  # healthy, degraded, down, unknown
    circuit_state: Mapped[str] = mapped_column(
        String(20), default="closed", nullable=False
    )  # closed, open, half_open
    last_health_check: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    avg_latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    risk_level: Mapped[str] = mapped_column(
        String(20), default="medium", nullable=False
    )  # low, medium, high

    __table_args__ = (
        Index("ix_connectors_slug", "slug"),
        Index("ix_connectors_type", "connector_type"),
        Index("ix_connectors_health", "health_status"),
    )


class ConnectorCall(Base):
    """Record of an individual call to an external connector."""

    __tablename__ = "connector_calls"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    connector_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True
    )
    run_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    task_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    operation: Mapped[str] = mapped_column(String(255), nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True
    )
    is_dry_run: Mapped[bool] = mapped_column(default=False, nullable=False)
    request_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    response_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # success, error, timeout, circuit_open
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_connector_calls_connector_id", "connector_id"),
        Index("ix_connector_calls_created_at", "created_at"),
        Index("ix_connector_calls_status", "status"),
    )
