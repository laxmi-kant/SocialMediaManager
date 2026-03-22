"""Celery tasks for comment fetching and auto-reply."""

import asyncio
from datetime import datetime, timedelta, timezone

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import joinedload

from app.config import settings
from app.models.comment import Comment
from app.models.platform_account import PlatformAccount
from app.models.published_post import PublishedPost
from app.services.comments.auto_reply import AutoReplyProcessor
from app.services.comments.fetcher import CommentFetcher
from app.tasks.celery_app import celery_app

logger = structlog.get_logger()


async def _fetch_comments():
    """Fetch new comments from all published posts."""
    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        # Get recently published LinkedIn posts
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        result = await session.execute(
            select(PublishedPost)
            .where(
                PublishedPost.status == "success",
                PublishedPost.published_at >= cutoff,
            )
            .options(joinedload(PublishedPost.platform_account))
        )
        posts = result.unique().scalars().all()

        fetcher = CommentFetcher(db=session)
        total = 0

        for pub_post in posts:
            account = pub_post.platform_account
            if not account or not account.is_active or account.platform != "linkedin":
                continue

            comments = await fetcher.fetch_comments_for_post(pub_post, account)
            total += len(comments)

        await session.commit()

    await engine.dispose()
    logger.info("comment_fetch_complete", total_new=total)


async def _auto_reply_comments():
    """Process unclassified/unreplied comments with AI."""
    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        # Find comments without replies
        result = await session.execute(
            select(Comment).where(
                Comment.sentiment.is_(None),
            ).limit(20)
        )
        comments = result.scalars().all()

        processor = AutoReplyProcessor(db=session)
        processed = 0

        for comment in comments:
            reply = await processor.process_comment(comment, auto_send=False)
            if reply:
                processed += 1

        await session.commit()

    await engine.dispose()
    logger.info("auto_reply_complete", processed=processed)


@celery_app.task(bind=True, max_retries=1)
def fetch_comments(self):
    """Celery task: fetch comments from platforms."""
    try:
        asyncio.run(_fetch_comments())
    except Exception as exc:
        logger.error("fetch_comments_error", error=str(exc))
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=1)
def auto_reply_comments(self):
    """Celery task: classify and generate replies for new comments."""
    try:
        asyncio.run(_auto_reply_comments())
    except Exception as exc:
        logger.error("auto_reply_error", error=str(exc))
        raise self.retry(exc=exc)
