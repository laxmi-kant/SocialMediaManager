"""Celery tasks for fetching analytics from social media platforms."""

import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import joinedload

from app.config import settings
from app.models.analytics_snapshot import AnalyticsSnapshot
from app.models.platform_account import PlatformAccount
from app.models.published_post import PublishedPost
from app.services.publishers.registry import publisher_registry
from app.tasks.celery_app import celery_app

logger = structlog.get_logger()


async def _fetch_analytics():
    """Fetch engagement metrics for recently published posts."""
    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        # Get published posts from the last 7 days
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        result = await session.execute(
            select(PublishedPost)
            .where(
                PublishedPost.status == "success",
                PublishedPost.published_at >= cutoff,
                PublishedPost.platform_post_id.isnot(None),
            )
            .options(joinedload(PublishedPost.platform_account))
        )
        posts = result.unique().scalars().all()

        if not posts:
            logger.info("no_posts_for_analytics")
            await engine.dispose()
            return

        logger.info("fetching_analytics", post_count=len(posts))

        for pub_post in posts:
            try:
                account = pub_post.platform_account
                if not account or not account.is_active:
                    continue

                publisher = publisher_registry.get(account.platform)
                metrics = await publisher.get_metrics(pub_post.platform_post_id, account)

                total_engagement = metrics.likes + metrics.comments + metrics.shares + metrics.clicks
                eng_rate = Decimal(str(
                    (total_engagement / metrics.impressions * 100) if metrics.impressions > 0 else 0
                )).quantize(Decimal("0.0001"))

                snapshot = AnalyticsSnapshot(
                    published_post_id=pub_post.id,
                    impressions=metrics.impressions,
                    likes=metrics.likes,
                    comments=metrics.comments,
                    shares=metrics.shares,
                    clicks=metrics.clicks,
                    engagement_rate=eng_rate,
                )
                session.add(snapshot)

            except Exception as exc:
                logger.warning("analytics_fetch_error", post_id=str(pub_post.id), error=str(exc))

        await session.commit()

    await engine.dispose()
    logger.info("analytics_fetch_complete")


@celery_app.task(bind=True, max_retries=1)
def fetch_analytics(self):
    """Celery task: fetch engagement metrics for recent posts."""
    try:
        asyncio.run(_fetch_analytics())
    except Exception as exc:
        logger.error("fetch_analytics_task_error", error=str(exc))
        raise self.retry(exc=exc)
