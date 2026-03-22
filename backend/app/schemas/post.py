"""Pydantic schemas for post endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class GeneratePostRequest(BaseModel):
    target_platform: str = Field(pattern="^(twitter|linkedin)$")
    content_type: str = Field(pattern="^(tech_insight|joke|news_commentary|github_spotlight|tip)$")
    tone: str = Field(default="professional", pattern="^(professional|casual|humorous|educational)$")


class UpdatePostRequest(BaseModel):
    content_text: str | None = None
    hashtags: list[str] | None = None
    tone: str | None = None


class SchedulePostRequest(BaseModel):
    scheduled_for: datetime


class ContentSourceBrief(BaseModel):
    id: uuid.UUID
    title: str
    url: str | None
    source_type: str

    model_config = {"from_attributes": True}


class PublishedPostBrief(BaseModel):
    id: uuid.UUID
    platform_post_id: str | None
    platform_url: str | None
    published_at: datetime | None
    status: str

    model_config = {"from_attributes": True}


class PostResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    content_source_id: uuid.UUID | None
    target_platform: str
    content_text: str
    content_type: str
    tone: str
    hashtags: list[str] | None
    ai_model: str | None
    token_usage: dict | None
    status: str
    scheduled_for: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    items: list[PostResponse]
    total: int
    page: int
    page_size: int
    pages: int
