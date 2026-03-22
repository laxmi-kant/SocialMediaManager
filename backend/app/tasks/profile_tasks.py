"""Celery tasks for LinkedIn profile intelligence collection."""

import asyncio

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings
from app.models.user import User
from app.services.profile_intelligence.manager import LeadManager
from app.tasks.celery_app import celery_app

logger = structlog.get_logger()


async def _collect_engager_profiles():
    """Collect engager profiles for all users."""
    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(select(User.id))
        user_ids = result.scalars().all()

        for user_id in user_ids:
            manager = LeadManager(session)
            total = await manager.collect_all_engagers(user_id)
            logger.info("user_engagers_collected", user_id=str(user_id), total=total)

    await engine.dispose()


async def _enrich_and_classify():
    """Enrich and classify unprocessed leads for all users."""
    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(select(User.id))
        user_ids = result.scalars().all()

        for user_id in user_ids:
            manager = LeadManager(session)
            processed = await manager.enrich_and_classify_leads(user_id)
            logger.info("user_leads_classified", user_id=str(user_id), processed=processed)

    await engine.dispose()


@celery_app.task(bind=True, max_retries=1)
def collect_engager_profiles(self):
    """Celery task: collect LinkedIn engager profiles."""
    try:
        asyncio.run(_collect_engager_profiles())
    except Exception as exc:
        logger.error("collect_engager_profiles_error", error=str(exc))
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=1)
def enrich_and_classify_leads(self):
    """Celery task: enrich profiles and classify lead status."""
    try:
        asyncio.run(_enrich_and_classify())
    except Exception as exc:
        logger.error("enrich_classify_error", error=str(exc))
        raise self.retry(exc=exc)
