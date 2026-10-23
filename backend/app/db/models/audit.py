"""Audit ledger ORM model with append-only constraints.

EPIC-03-T03: audit_ledger with hash-chain and monthly partitioning support.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.mixins import generate_uuid
from app.db.session import Base


class AuditLedgerEntry(Base):
    """Append-only, hash-chained audit ledger entry.

    Each entry references the hash of the previous entry to form
    a tamper-evident chain. No UPDATE or DELETE is permitted.
    """

    __tablename__ = "audit_ledger"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    sequence_number: Mapped[int] = mapped_column(
        nullable=False, unique=True, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    run_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    task_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    agent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    event_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # decision, action, approval, connector_call, error, etc.
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(nullable=True)
    model_used: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tokens_used: Mapped[int | None] = mapped_column(nullable=True)
    previous_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, default="0" * 64
    )
    entry_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True
    )

    __table_args__ = (
        Index("ix_audit_ledger_timestamp", "timestamp"),
        Index("ix_audit_ledger_event_type", "event_type"),
        Index("ix_audit_ledger_run_id_seq", "run_id", "sequence_number"),
    )
