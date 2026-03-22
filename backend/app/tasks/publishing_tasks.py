"""Celery tasks for publishing posts to social media platforms."""

import asyncio
from datetime import datetime, timezone

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models.generated_post import GeneratedPost
from app.models.platform_account import PlatformAccount
from app.models.published_post import PublishedPost
from app.services.publishers.registry import publisher_registry
from app.tasks.celery_app import celery_app

logger = structlog.get_logger()


async def _publish_single_post(session: AsyncSession, post: GeneratedPost) -> None:
    """Publish a single post to its target platform."""
    # Find the user's platform account
    result = await session.execute(
        select(PlatformAccount).where(
            PlatformAccount.user_id == post.user_id,
            PlatformAccount.platform == post.target_platform,
            PlatformAccount.is_active == True,
        )
    )
    account = result.scalar_one_or_none()
    if not account:
        logger.warning("no_platform_account", post_id=str(post.id), platform=post.target_platform)
        post.status = "failed"
        db_published = PublishedPost(
            generated_post_id=post.id,
            platform_account_id=account.id if account else post.user_id,  # fallback
            status="failed",
            error_message=f"No active {post.target_platform} account connected",
        )
        session.add(db_published)
        return

    publisher = publisher_registry.get(post.target_platform)
    pub_result = await publisher.publish(
        text=post.content_text,
        hashtags=post.hashtags or [],
        account=account,
    )

    if pub_result.success:
        post.status = "published"
        db_published = PublishedPost(
            generated_post_id=post.id,
            platform_account_id=account.id,
            platform_post_id=pub_result.platform_post_id,
            platform_url=pub_result.platform_url,
            status="success",
        )
    else:
        post.status = "failed"
        db_published = PublishedPost(
            generated_post_id=post.id,
            platform_account_id=account.id,
            status="failed",
            error_message=pub_result.error_message,
        )

    session.add(db_published)
    logger.info(
        "post_publish_result",
        post_id=str(post.id),
        success=pub_result.success,
        platform=post.target_platform,
    )


async def _publish_scheduled_posts():
    """Find and publish all posts that are due."""
    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        now = datetime.now(timezone.utc)
        result = await session.execute(
            select(GeneratedPost).where(
                GeneratedPost.status == "scheduled",
                GeneratedPost.scheduled_for <= now,
            )
        )
        posts = result.scalars().all()

        if not posts:
            return

        logger.info("publishing_scheduled_posts", count=len(posts))

        for post in posts:
            try:
                await _publish_single_post(session, post)
            except Exception as exc:
                logger.error("scheduled_publish_error", post_id=str(post.id), error=str(exc))
                post.status = "failed"

        await session.commit()

    await engine.dispose()


@celery_app.task(bind=True, max_retries=2, default_retry_delay=120)
def publish_scheduled_posts(self):
    """Celery task: publish all scheduled posts that are due."""
    try:
        asyncio.run(_publish_scheduled_posts())
    except Exception as exc:
        logger.error("publish_scheduled_task_error", error=str(exc))
        raise self.retry(exc=exc)


async def _publish_post_now(generated_post_id: str, user_id: str):
    """Publish a single post immediately (async)."""
    import uuid
    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(
            select(GeneratedPost).where(
                GeneratedPost.id == uuid.UUID(generated_post_id),
                GeneratedPost.user_id == uuid.UUID(user_id),
            )
        )
        post = result.scalar_one_or_none()
        if not post:
            logger.error("post_not_found_for_publish", post_id=generated_post_id)
            return

        await _publish_single_post(session, post)
        await session.commit()

    await engine.dispose()


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def publish_post_now_task(self, generated_post_id: str, user_id: str):
    """Celery task: publish a single post immediately."""
    try:
        asyncio.run(_publish_post_now(generated_post_id, user_id))
    except Exception as exc:
        logger.error("publish_now_task_error", error=str(exc), post_id=generated_post_id)
        raise self.retry(exc=exc)
