"""Approval ORM models.

EPIC-03-T04: approval_requests, approval_decisions.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.mixins import TimestampMixin, generate_uuid
from app.db.session import Base


class ApprovalRequest(TimestampMixin, Base):
    """An approval request created when a policy requires human sign-off."""

    __tablename__ = "approval_requests"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False
    )
    task_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )
    policy_id: Mapped[str | None] = mapped_column(
        String(36), nullable=True
    )
    approval_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # approval, dual_approval, notify
    risk_level: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # low, medium, high, critical
    status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False
    )  # pending, approved, rejected, expired, escalated
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    diff_before: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    diff_after: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    diff_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    timeout_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    escalation_target: Mapped[str | None] = mapped_column(String(36), nullable=True)
    required_approvals: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    decisions: Mapped[list[ApprovalDecision]] = relationship(
        "ApprovalDecision",
        back_populates="request",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_approval_requests_status", "status"),
        Index("ix_approval_requests_run_id", "run_id"),
        Index("ix_approval_requests_created_at", "created_at"),
    )


class ApprovalDecision(TimestampMixin, Base):
    """A decision made by an approver on an approval request."""

    __tablename__ = "approval_decisions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    request_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("approval_requests.id", ondelete="CASCADE"),
        nullable=False,
    )
    approver_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    decision: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # approved, rejected
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    edited_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    request: Mapped[ApprovalRequest] = relationship(
        "ApprovalRequest", back_populates="decisions"
    )

    __table_args__ = (
        Index("ix_approval_decisions_request_id", "request_id"),
        Index("ix_approval_decisions_approver_id", "approver_id"),
    )
