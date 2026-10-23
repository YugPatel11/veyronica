"""Document and knowledge base ORM models.

EPIC-03-T09: documents, chunks (pgvector), question_bank.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.mixins import TimestampMixin, generate_uuid
from app.db.session import Base


class Document(TimestampMixin, Base):
    """Uploaded document (syllabus, answer sheet, etc.)."""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    document_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # syllabus, answer_sheet, rubric, template
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    uploaded_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    # Relationships
    chunks: Mapped[list[DocumentChunk]] = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    __table_args__ = (
        Index("ix_documents_type", "document_type"),
        Index("ix_documents_content_hash", "content_hash"),
    )


class DocumentChunk(Base):
    """Embedded chunk of a document for semantic search.

    Note: The `embedding` column uses pgvector's VECTOR type.
    We store it as Text here and use raw SQL for vector operations
    since SQLAlchemy pgvector support varies. The actual migration
    will create the column with the correct type.
    """

    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    document_id: Mapped[str] = mapped_column(
        String(36), nullable=False, index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    # embedding: vector(1536) — created via raw SQL in migration
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    document: Mapped[Document] = relationship("Document", back_populates="chunks")

    __table_args__ = (
        Index("ix_document_chunks_doc_index", "document_id", "chunk_index"),
    )


class QuestionBankItem(TimestampMixin, Base):
    """Generated or curated question for the question bank."""

    __tablename__ = "question_bank"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid
    )
    document_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(255), nullable=True)
    difficulty: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # easy, medium, hard
    bloom_level: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # remember, understand, apply, analyze, evaluate, create
    marks: Mapped[int] = mapped_column(Integer, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    answer_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    marking_scheme: Mapped[str | None] = mapped_column(Text, nullable=True)
    originality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    generated_by_model: Mapped[str | None] = mapped_column(String(100), nullable=True)

    __table_args__ = (
        Index("ix_question_bank_subject", "subject"),
        Index("ix_question_bank_difficulty", "difficulty"),
        Index("ix_question_bank_bloom", "bloom_level"),
    )
