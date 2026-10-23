"""Policy ORM model.

EPIC-03-T07: policies table (versioned YAML).
"""

from __future__ import annotations

from sqlalchemy import Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.mixins import TimestampMixin, generate_uuid
from app.db.session import Base


class Policy(TimestampMixin, Base):
    """Versioned policy rule definition."""

    __tablename__ = "policies"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # marks, delete, communication, leave, security
    yaml_content: Mapped[str] = mapped_column(Text, nullable=False)
    compiled_rules: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_by: Mapped[str | None] = mapped_column(String(36), nullable=True)

    __table_args__ = (
        Index("ix_policies_slug_version", "slug", "version", unique=True),
        Index("ix_policies_category", "category"),
        Index("ix_policies_active", "is_active"),
    )
