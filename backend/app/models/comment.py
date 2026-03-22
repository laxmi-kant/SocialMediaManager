"""Comment and comment reply models (fetched from platforms, AI-managed)."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = (UniqueConstraint("platform", "platform_comment_id", name="uq_comments_platform_comment"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    published_post_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("published_posts.id", ondelete="CASCADE"), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    platform_comment_id: Mapped[str] = mapped_column(String(255), nullable=False)
    commenter_name: Mapped[str | None] = mapped_column(String(255))
    commenter_username: Mapped[str | None] = mapped_column(String(255))
    commenter_profile_url: Mapped[str | None] = mapped_column(Text)
    commenter_follower_count: Mapped[int | None] = mapped_column(Integer)
    comment_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_mention: Mapped[bool] = mapped_column(Boolean, default=False)
    is_reply_to_reply: Mapped[bool] = mapped_column(Boolean, default=False)
    parent_comment_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("comments.id"))
    sentiment: Mapped[str | None] = mapped_column(String(20))
    comment_type: Mapped[str | None] = mapped_column(String(30))
    commented_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    published_post = relationship("PublishedPost", back_populates="comments")
    replies = relationship("CommentReply", back_populates="comment", cascade="all, delete-orphan")
    parent_comment = relationship("Comment", remote_side="Comment.id", backref="child_comments")


class CommentReply(Base):
    __tablename__ = "comment_replies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("comments.id", ondelete="CASCADE"), nullable=False, index=True)
    reply_text: Mapped[str] = mapped_column(Text, nullable=False)
    ai_suggested_text: Mapped[str | None] = mapped_column(Text)
    ai_model: Mapped[str | None] = mapped_column(String(100))
    token_usage: Mapped[dict | None] = mapped_column(JSONB)
    reply_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="draft", index=True)
    platform_reply_id: Mapped[str | None] = mapped_column(String(255))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    comment = relationship("Comment", back_populates="replies")
