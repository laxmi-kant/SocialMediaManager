"""Generated post model (AI-created content in various workflow states)."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class GeneratedPost(Base):
    __tablename__ = "generated_posts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content_source_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("content_sources.id", ondelete="SET NULL"))
    target_platform: Mapped[str] = mapped_column(String(50), nullable=False)
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    tone: Mapped[str] = mapped_column(String(50), default="professional")
    hashtags: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    ai_model: Mapped[str | None] = mapped_column(String(100))
    prompt_used: Mapped[str | None] = mapped_column(Text)
    token_usage: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(30), default="draft", index=True)
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    schedule_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("schedules.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="generated_posts")
    content_source = relationship("ContentSource", back_populates="generated_posts")
    schedule = relationship("Schedule", back_populates="generated_posts")
    published_posts = relationship("PublishedPost", back_populates="generated_post", cascade="all, delete-orphan")
