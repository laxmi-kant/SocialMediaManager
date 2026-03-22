"""Dev.to content source client."""

from app.services.content_research.base import ContentItem, ContentSourceBase

API_URL = "https://dev.to/api/articles"


class DevToClient(ContentSourceBase):
    source_type = "devto"

    async def fetch_trending(self, limit: int = 20) -> list[ContentItem]:
        resp = await self._http_client.get(API_URL, params={"top": 1, "per_page": limit})
        articles = resp.json()

        return [
            ContentItem(
                source_type=self.source_type,
                external_id=str(a["id"]),
                title=a["title"],
                url=a["url"],
                content=a.get("description", ""),
                author=a.get("user", {}).get("username"),
                score=a.get("positive_reactions_count", 0),
                tags=[t for t in a.get("tag_list", [])],
                metadata={
                    "reading_time": a.get("reading_time_minutes"),
                    "comments_count": a.get("comments_count", 0),
                },
            )
            for a in articles
        ]
