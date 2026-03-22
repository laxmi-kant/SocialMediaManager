"""Analytics API routes - engagement metrics and summaries."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.api.deps import get_current_user
from app.database import get_db
from app.models.analytics_snapshot import AnalyticsSnapshot
from app.models.generated_post import GeneratedPost
from app.models.published_post import PublishedPost
from app.models.user import User
from app.schemas.analytics import AnalyticsSummary, PostAnalytics

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=AnalyticsSummary)
async def get_analytics(
    days: int = Query(default=30, ge=1, le=365),
    platform: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    # Get published posts for this user
    query = (
        select(PublishedPost)
        .join(GeneratedPost, PublishedPost.generated_post_id == GeneratedPost.id)
        .where(
            GeneratedPost.user_id == user.id,
            PublishedPost.status == "success",
            PublishedPost.published_at >= cutoff,
        )
        .options(
            joinedload(PublishedPost.generated_post),
            joinedload(PublishedPost.analytics_snapshots),
        )
    )
    if platform:
        query = query.where(GeneratedPost.target_platform == platform)

    result = await db.execute(query)
    published_posts = result.unique().scalars().all()

    posts_analytics = []
    total_impressions = 0
    total_likes = 0
    total_comments = 0
    total_shares = 0

    for pub in published_posts:
        # Get the latest snapshot
        snapshots = sorted(pub.analytics_snapshots, key=lambda s: s.snapshot_at, reverse=True)
        latest = snapshots[0] if snapshots else None

        impressions = latest.impressions if latest else 0
        likes = latest.likes if latest else 0
        comments = latest.comments if latest else 0
        shares = latest.shares if latest else 0
        clicks = latest.clicks if latest else 0

        total_impressions += impressions
        total_likes += likes
        total_comments += comments
        total_shares += shares

        eng = latest.engagement_rate if latest else None

        posts_analytics.append(PostAnalytics(
            post_id=pub.generated_post_id,
            platform=pub.generated_post.target_platform,
            content_text=pub.generated_post.content_text[:100],
            published_at=pub.published_at,
            platform_url=pub.platform_url,
            impressions=impressions,
            likes=likes,
            comments=comments,
            shares=shares,
            clicks=clicks,
            engagement_rate=eng,
        ))

    total_engagement = total_likes + total_comments + total_shares
    avg_rate = (total_engagement / total_impressions * 100) if total_impressions > 0 else 0.0

    return AnalyticsSummary(
        total_posts=len(published_posts),
        total_impressions=total_impressions,
        total_likes=total_likes,
        total_comments=total_comments,
        total_shares=total_shares,
        avg_engagement_rate=round(avg_rate, 2),
        posts=sorted(posts_analytics, key=lambda p: p.likes, reverse=True),
    )
