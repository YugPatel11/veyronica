"""Agent registry ORM model.

EPIC-03-T02 (part of agents table).
"""

from __future__ import annotations

from sqlalchemy import Boolean, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.mixins import TimestampMixin, generate_uuid
from app.db.session import Base


class Agent(TimestampMixin, Base):
    """Registered agent in the platform."""

    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    agent_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # master, ingestion, evaluation, analysis, communication, verifier, copilot, security
    default_model_tier: Mapped[str] = mapped_column(
        String(50), default="standard", nullable=False
    )  # economy, standard, premium
    tools: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    max_concurrent: Mapped[int] = mapped_column(Integer, default=5, nullable=False)

    __table_args__ = (
        Index("ix_agents_slug", "slug"),
        Index("ix_agents_type", "agent_type"),
        Index("ix_agents_active", "is_active"),
    )
