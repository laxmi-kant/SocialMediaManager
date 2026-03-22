"""Hacker News content source client."""

import asyncio

import structlog

from app.services.content_research.base import ContentItem, ContentSourceBase

logger = structlog.get_logger()

BASE_URL = "https://hacker-news.firebaseio.com/v0"


class HackerNewsClient(ContentSourceBase):
    source_type = "hackernews"

    async def fetch_trending(self, limit: int = 30) -> list[ContentItem]:
        resp = await self._http_client.get(f"{BASE_URL}/topstories.json")
        story_ids = resp.json()[:limit]

        tasks = [self._get_story(sid) for sid in story_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        items = []
        for result in results:
            if isinstance(result, ContentItem):
                items.append(result)
            elif isinstance(result, Exception):
                logger.warning("hn_story_fetch_failed", error=str(result))
        return items

    async def _get_story(self, story_id: int) -> ContentItem:
        resp = await self._http_client.get(f"{BASE_URL}/item/{story_id}.json")
        data = resp.json()
        return ContentItem(
            source_type=self.source_type,
            external_id=str(data["id"]),
            title=data.get("title", ""),
            url=data.get("url"),
            content=data.get("text"),
            author=data.get("by"),
            score=data.get("score", 0),
            tags=[],
            metadata={
                "hn_id": data["id"],
                "num_comments": data.get("descendants", 0),
                "story_type": data.get("type", "story"),
            },
        )
