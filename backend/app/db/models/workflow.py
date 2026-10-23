"""Workflow-related ORM models.

EPIC-03-T02: agents, workflow_definitions, workflow_runs, tasks, task_events.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.mixins import TimestampMixin, generate_uuid
from app.db.session import Base


class WorkflowDefinition(TimestampMixin, Base):
    """Versioned workflow YAML definition."""

    __tablename__ = "workflow_definitions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    yaml_content: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # Relationships
    runs: Mapped[list[WorkflowRun]] = relationship(
        "WorkflowRun", back_populates="definition", lazy="dynamic"
    )

    __table_args__ = (
        Index("ix_workflow_definitions_slug", "slug"),
        Index("ix_workflow_definitions_active", "is_active"),
    )


class WorkflowRun(TimestampMixin, Base):
    """Single execution of a workflow."""

    __tablename__ = "workflow_runs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    definition_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("workflow_definitions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False
    )  # pending, running, waiting_approval, completed, failed, cancelled
    trigger_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # manual, webhook, scheduled, copilot
    trigger_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    autonomy_level: Mapped[str] = mapped_column(
        String(20), default="supervised", nullable=False
    )  # assist, supervised, autonomous
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    initiated_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    definition: Mapped[WorkflowDefinition] = relationship(
        "WorkflowDefinition", back_populates="runs"
    )
    tasks: Mapped[list[Task]] = relationship(
        "Task", back_populates="run", cascade="all, delete-orphan", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_workflow_runs_status", "status"),
        Index("ix_workflow_runs_definition_id", "definition_id"),
        Index("ix_workflow_runs_created_at", "created_at"),
    )


class Task(TimestampMixin, Base):
    """Individual task within a workflow run, executed by an agent."""

    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    run_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("workflow_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    agent_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("agents.id"), nullable=True
    )
    step_name: Mapped[str] = mapped_column(String(255), nullable=False)
    step_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # agent, approval, branch, parallel
    status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False
    )  # pending, running, waiting_approval, completed, failed, skipped
    input_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    output_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    run: Mapped[WorkflowRun] = relationship("WorkflowRun", back_populates="tasks")
    agent: Mapped[Agent | None] = relationship("Agent", lazy="selectin")
    events: Mapped[list[TaskEvent]] = relationship(
        "TaskEvent", back_populates="task", cascade="all, delete-orphan", lazy="dynamic"
    )

    __table_args__ = (
        Index("ix_tasks_run_id", "run_id"),
        Index("ix_tasks_status", "status"),
        Index("ix_tasks_agent_id", "agent_id"),
    )


class TaskEvent(TimestampMixin, Base):
    """Event log for task state transitions and actions."""

    __tablename__ = "task_events"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    task_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # status_change, llm_call, connector_call, approval_requested, error, etc.
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    task: Mapped[Task] = relationship("Task", back_populates="events")

    __table_args__ = (
        Index("ix_task_events_task_id", "task_id"),
        Index("ix_task_events_type", "event_type"),
        Index("ix_task_events_timestamp", "timestamp"),
    )
