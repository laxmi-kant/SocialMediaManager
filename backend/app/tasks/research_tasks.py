"""Celery tasks for content research."""

import asyncio

import structlog
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.services.content_research.aggregator import ContentAggregator
from app.services.content_research.devto import DevToClient
from app.services.content_research.github_trending import GitHubTrendingClient
from app.services.content_research.hackernews import HackerNewsClient
from app.services.content_research.jokes import JokeClient
from app.services.content_research.reddit import RedditClient
from app.tasks.celery_app import celery_app

logger = structlog.get_logger()


def _get_session() -> AsyncSession:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return session_factory()


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def fetch_trending_content(self):
    """Fetch trending content from all sources."""
    return asyncio.run(_fetch_trending())


async def _fetch_trending() -> dict:
    sources = [
        HackerNewsClient(),
        DevToClient(),
        JokeClient(),
        GitHubTrendingClient(),
    ]

    # Only add Reddit if credentials are configured
    if settings.reddit_client_id and settings.reddit_client_secret:
        sources.append(RedditClient())

    async with _get_session() as db:
        aggregator = ContentAggregator(sources=sources, db=db)
        try:
            result = await aggregator.fetch_all(limit_per_source=20)
            return {
                "total": result.total_items,
                "new": result.new_items,
                "errors": result.errors,
            }
        finally:
            await aggregator.close()
