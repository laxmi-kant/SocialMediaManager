"""Dashboard API route - aggregated stats for the dashboard page."""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.analytics_snapshot import AnalyticsSnapshot
from app.models.generated_post import GeneratedPost
from app.models.published_post import PublishedPost
from app.models.user import User
from app.schemas.analytics import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardStats)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Count posts by status
    status_counts = {}
    for s in ["draft", "approved", "scheduled", "published", "rejected", "failed"]:
        result = await db.execute(
            select(func.count()).select_from(GeneratedPost).where(
                GeneratedPost.user_id == user.id,
                GeneratedPost.status == s,
            )
        )
        status_counts[s] = result.scalar_one()

    total_posts = sum(status_counts.values())

    # Get aggregate analytics
    result = await db.execute(
        select(
            func.coalesce(func.sum(AnalyticsSnapshot.impressions), 0),
            func.coalesce(func.sum(AnalyticsSnapshot.likes), 0),
        )
        .select_from(AnalyticsSnapshot)
        .join(PublishedPost, AnalyticsSnapshot.published_post_id == PublishedPost.id)
        .join(GeneratedPost, PublishedPost.generated_post_id == GeneratedPost.id)
        .where(GeneratedPost.user_id == user.id)
    )
    row = result.one()
    total_impressions = int(row[0])
    total_likes = int(row[1])

    # Avg engagement rate from latest snapshots
    avg_rate = (total_likes / total_impressions * 100) if total_impressions > 0 else 0.0

    # Recent published posts (last 5)
    recent_result = await db.execute(
        select(GeneratedPost)
        .where(GeneratedPost.user_id == user.id, GeneratedPost.status == "published")
        .order_by(GeneratedPost.updated_at.desc())
        .limit(5)
    )
    recent = [
        {
            "id": str(p.id),
            "platform": p.target_platform,
            "text": p.content_text[:80],
            "status": p.status,
            "updated_at": p.updated_at.isoformat(),
        }
        for p in recent_result.scalars().all()
    ]

    # Upcoming scheduled posts (next 5)
    now = datetime.now(timezone.utc)
    upcoming_result = await db.execute(
        select(GeneratedPost)
        .where(
            GeneratedPost.user_id == user.id,
            GeneratedPost.status == "scheduled",
            GeneratedPost.scheduled_for >= now,
        )
        .order_by(GeneratedPost.scheduled_for.asc())
        .limit(5)
    )
    upcoming = [
        {
            "id": str(p.id),
            "platform": p.target_platform,
            "text": p.content_text[:80],
            "scheduled_for": p.scheduled_for.isoformat() if p.scheduled_for else None,
        }
        for p in upcoming_result.scalars().all()
    ]

    return DashboardStats(
        total_posts=total_posts,
        published_posts=status_counts.get("published", 0),
        scheduled_posts=status_counts.get("scheduled", 0),
        draft_posts=status_counts.get("draft", 0),
        total_impressions=total_impressions,
        total_likes=total_likes,
        avg_engagement_rate=round(avg_rate, 2),
        recent_posts=recent,
        upcoming_posts=upcoming,
    )
