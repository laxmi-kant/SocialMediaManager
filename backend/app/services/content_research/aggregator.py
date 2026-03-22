"""Content aggregator - runs all sources concurrently and upserts results."""

import asyncio
from dataclasses import dataclass, field

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_source import ContentSource
from app.services.content_research.base import ContentItem, ContentSourceBase

logger = structlog.get_logger()


@dataclass
class AggregationResult:
    total_items: int = 0
    new_items: int = 0
    updated_items: int = 0
    errors: list[str] = field(default_factory=list)


class ContentAggregator:
    """Fetches from all sources concurrently and bulk upserts to DB."""

    def __init__(self, sources: list[ContentSourceBase], db: AsyncSession):
        self.sources = sources
        self.db = db

    async def fetch_all(self, limit_per_source: int = 20) -> AggregationResult:
        result = AggregationResult()

        # Fetch from all sources concurrently
        tasks = [self._safe_fetch(source, limit_per_source) for source in self.sources]
        source_results = await asyncio.gather(*tasks)

        all_items: list[ContentItem] = []
        for items, error in source_results:
            if error:
                result.errors.append(error)
            all_items.extend(items)

        result.total_items = len(all_items)

        # Bulk upsert
        if all_items:
            result.new_items = await self._bulk_upsert(all_items)

        logger.info(
            "aggregation_complete",
            total=result.total_items,
            new=result.new_items,
            errors=len(result.errors),
        )
        return result

    async def _safe_fetch(
        self, source: ContentSourceBase, limit: int
    ) -> tuple[list[ContentItem], str | None]:
        try:
            items = await source.fetch_trending(limit)
            logger.info("source_fetched", source=source.source_type, count=len(items))
            return items, None
        except Exception as e:
            error_msg = f"{source.source_type}: {e}"
            logger.error("source_fetch_failed", source=source.source_type, error=str(e))
            return [], error_msg

    async def _bulk_upsert(self, items: list[ContentItem]) -> int:
        """Upsert content items using ON CONFLICT DO UPDATE."""
        new_count = 0
        for item in items:
            stmt = text("""
                INSERT INTO content_sources (source_type, external_id, title, url, content, author, score, tags, metadata, fetched_at)
                VALUES (:source_type, :external_id, :title, :url, :content, :author, :score, :tags, :metadata::jsonb, NOW())
                ON CONFLICT (source_type, external_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    score = EXCLUDED.score,
                    content = EXCLUDED.content,
                    metadata = EXCLUDED.metadata,
                    fetched_at = NOW()
                RETURNING (xmax = 0) AS is_new
            """)
            result = await self.db.execute(stmt, {
                "source_type": item.source_type,
                "external_id": item.external_id,
                "title": item.title,
                "url": item.url,
                "content": item.content,
                "author": item.author,
                "score": item.score,
                "tags": item.tags,
                "metadata": str(item.metadata).replace("'", '"') if item.metadata else "{}",
            })
            row = result.fetchone()
            if row and row.is_new:
                new_count += 1

        await self.db.commit()
        return new_count

    async def close(self):
        for source in self.sources:
            await source.close()
