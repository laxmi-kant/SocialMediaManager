"""Published post model (posts sent to platforms)."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class PublishedPost(Base):
    __tablename__ = "published_posts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    generated_post_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("generated_posts.id", ondelete="CASCADE"), nullable=False, index=True)
    platform_account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("platform_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    platform_post_id: Mapped[str | None] = mapped_column(String(255))
    platform_url: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[str] = mapped_column(String(30), default="success")
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    generated_post = relationship("GeneratedPost", back_populates="published_posts")
    platform_account = relationship("PlatformAccount", back_populates="published_posts")
    analytics_snapshots = relationship("AnalyticsSnapshot", back_populates="published_post", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="published_post", cascade="all, delete-orphan")
