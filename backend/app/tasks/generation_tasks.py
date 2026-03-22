"""Celery tasks for AI content generation."""

import asyncio
import random
import uuid
from datetime import datetime, timezone

import structlog
from croniter import croniter
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models.content_source import ContentSource
from app.models.generated_post import GeneratedPost
from app.models.schedule import Schedule
from app.services.ai_generator.generator import PostGenerator
from app.tasks.celery_app import celery_app

logger = structlog.get_logger()


def _get_session() -> AsyncSession:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return session_factory()


@celery_app.task(bind=True, max_retries=1, default_retry_delay=30)
def generate_post(self, content_source_id: str, target_platform: str, content_type: str, tone: str, user_id: str):
    """Generate a single post from content source."""
    return asyncio.run(_generate_post(content_source_id, target_platform, content_type, tone, user_id))


async def _generate_post(content_source_id: str, target_platform: str, content_type: str, tone: str, user_id: str) -> dict:
    async with _get_session() as db:
        generator = PostGenerator(db=db)
        post = await generator.generate_post(
            content_source_id=uuid.UUID(content_source_id),
            target_platform=target_platform,
            content_type=content_type,
            tone=tone,
            user_id=uuid.UUID(user_id),
        )
        await db.commit()
        return {"post_id": str(post.id)}


async def _process_active_schedules():
    """Check all active schedules and generate content for any that are due."""
    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(
            select(Schedule).where(Schedule.is_active == True)
        )
        schedules = result.scalars().all()

        if not schedules:
            await engine.dispose()
            return {"processed": 0}

        processed = 0
        now = datetime.now(timezone.utc)

        for schedule in schedules:
            try:
                # Check if schedule is due based on cron expression
                cron = croniter(schedule.cron_expression, now)
                prev_fire = cron.get_prev(datetime)

                # Check if we already generated a post since the last fire time
                existing = await session.execute(
                    select(func.count()).select_from(GeneratedPost).where(
                        GeneratedPost.schedule_id == schedule.id,
                        GeneratedPost.created_at >= prev_fire,
                    )
                )
                if existing.scalar_one() > 0:
                    continue  # Already generated for this interval

                # Pick a random content type from the schedule
                content_type = random.choice(schedule.content_types)

                # Pick a recent content source
                source_result = await session.execute(
                    select(ContentSource)
                    .order_by(ContentSource.fetched_at.desc())
                    .limit(20)
                )
                sources = source_result.scalars().all()
                if not sources:
                    logger.warning("no_content_sources_for_schedule", schedule_id=str(schedule.id))
                    continue

                source = random.choice(sources)

                # Generate the post
                generator = PostGenerator(db=session)
                post = await generator.generate_post(
                    content_source_id=source.id,
                    target_platform=schedule.platform,
                    content_type=content_type,
                    tone="professional",
                    user_id=schedule.user_id,
                )
                post.schedule_id = schedule.id

                # Auto-approve if configured
                if schedule.auto_approve:
                    post.status = "approved"

                processed += 1
                logger.info(
                    "schedule_generated_post",
                    schedule_id=str(schedule.id),
                    post_id=str(post.id),
                    auto_approved=schedule.auto_approve,
                )

            except Exception as exc:
                logger.error("schedule_processing_error", schedule_id=str(schedule.id), error=str(exc))

        await session.commit()

    await engine.dispose()
    return {"processed": processed}


@celery_app.task(bind=True)
def process_active_schedules(self):
    """Check active schedules and generate content if due."""
    return asyncio.run(_process_active_schedules())
