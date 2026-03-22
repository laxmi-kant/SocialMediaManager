"""Content source model (Hacker News, Reddit, Dev.to, Jokes, GitHub)."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class ContentSource(Base):
    __tablename__ = "content_sources"
    __table_args__ = (UniqueConstraint("source_type", "external_id", name="uq_content_sources_type_external"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str | None] = mapped_column(Text)
    author: Mapped[str | None] = mapped_column(String(255))
    score: Mapped[int] = mapped_column(Integer, default=0)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, default=dict)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    generated_posts = relationship("GeneratedPost", back_populates="content_source")
