"""Pydantic schemas for analytics endpoints."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class AnalyticsSnapshotResponse(BaseModel):
    id: uuid.UUID
    published_post_id: uuid.UUID
    impressions: int
    likes: int
    comments: int
    shares: int
    clicks: int
    engagement_rate: Decimal | None
    snapshot_at: datetime

    model_config = {"from_attributes": True}


class PostAnalytics(BaseModel):
    post_id: uuid.UUID
    platform: str
    content_text: str
    published_at: datetime | None
    platform_url: str | None
    impressions: int
    likes: int
    comments: int
    shares: int
    clicks: int
    engagement_rate: Decimal | None


class AnalyticsSummary(BaseModel):
    total_posts: int
    total_impressions: int
    total_likes: int
    total_comments: int
    total_shares: int
    avg_engagement_rate: float
    posts: list[PostAnalytics]


class DashboardStats(BaseModel):
    total_posts: int
    published_posts: int
    scheduled_posts: int
    draft_posts: int
    total_impressions: int
    total_likes: int
    avg_engagement_rate: float
    recent_posts: list[dict]
    upcoming_posts: list[dict]
