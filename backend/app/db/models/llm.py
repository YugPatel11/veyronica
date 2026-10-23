"""LLM Gateway ORM models.

EPIC-03-T05: llm_calls, token_budgets, model_tiers.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.mixins import TimestampMixin, generate_uuid
from app.db.session import Base


class LLMCall(Base):
    """Record of a single LLM API call (usage logging)."""

    __tablename__ = "llm_calls"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    run_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    task_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    agent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_tier: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # economy, standard, premium
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # openai, anthropic, google
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Float, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    cached: Mapped[bool] = mapped_column(default=False, nullable=False)
    prompt_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="success", nullable=False
    )  # success, error, timeout
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_llm_calls_created_at", "created_at"),
        Index("ix_llm_calls_model_tier", "model_tier"),
        Index("ix_llm_calls_run_agent", "run_id", "agent_id"),
    )


class TokenBudget(TimestampMixin, Base):
    """Token budget configuration at various scopes."""

    __tablename__ = "token_budgets"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    scope: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # global, workflow, agent, task
    scope_id: Mapped[str | None] = mapped_column(
        String(36), nullable=True
    )  # null for global scope
    daily_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    monthly_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    daily_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    monthly_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    daily_cost_limit_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    monthly_cost_limit_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    alert_threshold_pct: Mapped[int] = mapped_column(
        Integer, default=80, nullable=False
    )

    __table_args__ = (
        Index("ix_token_budgets_scope", "scope", "scope_id"),
    )


class ModelTier(TimestampMixin, Base):
    """LLM model tier configuration with pricing."""

    __tablename__ = "model_tiers"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    tier: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # economy, standard, premium
    model_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    input_cost_per_1k: Mapped[float] = mapped_column(Float, nullable=False)
    output_cost_per_1k: Mapped[float] = mapped_column(Float, nullable=False)
    max_context_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    __table_args__ = (
        Index("ix_model_tiers_tier", "tier"),
    )
