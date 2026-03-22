"""LinkedIn lead and engagement models for profile intelligence."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class LinkedInLead(Base):
    __tablename__ = "linkedin_leads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    linkedin_member_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(255))
    headline: Mapped[str | None] = mapped_column(Text)
    current_company: Mapped[str | None] = mapped_column(String(255))
    profile_url: Mapped[str | None] = mapped_column(Text)
    email: Mapped[str | None] = mapped_column(String(255))
    location: Mapped[str | None] = mapped_column(String(255))
    industry: Mapped[str | None] = mapped_column(String(255))
    ai_status: Mapped[str | None] = mapped_column(String(50))  # OPEN_TO_WORK, HIRING, BUSINESS, GENERAL
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="leads")
    engagements = relationship("LeadEngagement", back_populates="lead", cascade="all, delete-orphan")


class LeadEngagement(Base):
    __tablename__ = "lead_engagements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("linkedin_leads.id", ondelete="CASCADE"), nullable=False, index=True)
    published_post_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("published_posts.id", ondelete="CASCADE"), nullable=False)
    engagement_type: Mapped[str] = mapped_column(String(30), nullable=False)  # like, comment, share
    engagement_text: Mapped[str | None] = mapped_column(Text)
    engaged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    lead = relationship("LinkedInLead", back_populates="engagements")
    published_post = relationship("PublishedPost")
