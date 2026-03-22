"""Reddit content source client with OAuth."""

import structlog

from app.config import settings
from app.services.content_research.base import ContentItem, ContentSourceBase
from app.utils.http_client import ResilientHTTPClient

logger = structlog.get_logger()

AUTH_URL = "https://www.reddit.com/api/v1/access_token"
API_URL = "https://oauth.reddit.com"
SUBREDDITS = ["technology", "programming", "webdev"]


class RedditClient(ContentSourceBase):
    source_type = "reddit"

    def __init__(self):
        super().__init__()
        self._access_token: str | None = None

    async def _authenticate(self) -> str:
        """Get OAuth access token using client credentials."""
        if not settings.reddit_client_id or not settings.reddit_client_secret:
            raise ValueError("Reddit OAuth credentials not configured")

        auth_client = ResilientHTTPClient(service_name="reddit", headers={"User-Agent": "SMM/1.0"})
        try:
            resp = await auth_client.post(
                AUTH_URL,
                data={"grant_type": "client_credentials"},
                auth=(settings.reddit_client_id, settings.reddit_client_secret),
            )
            data = resp.json()
            self._access_token = data["access_token"]
            return self._access_token
        finally:
            await auth_client.close()

    async def fetch_trending(self, limit: int = 20) -> list[ContentItem]:
        token = self._access_token or await self._authenticate()
        per_sub = max(5, limit // len(SUBREDDITS))
        items: list[ContentItem] = []

        for subreddit in SUBREDDITS:
            try:
                resp = await self._http_client.get(
                    f"{API_URL}/r/{subreddit}/hot.json",
                    params={"limit": per_sub},
                    headers={"Authorization": f"Bearer {token}", "User-Agent": "SMM/1.0"},
                )
                data = resp.json()
                for post in data.get("data", {}).get("children", []):
                    p = post["data"]
                    if p.get("stickied"):
                        continue
                    items.append(ContentItem(
                        source_type=self.source_type,
                        external_id=p["id"],
                        title=p["title"],
                        url=f"https://reddit.com{p['permalink']}",
                        content=p.get("selftext", "")[:500] or None,
                        author=p.get("author"),
                        score=p.get("score", 0),
                        tags=[subreddit],
                        metadata={
                            "subreddit": subreddit,
                            "permalink": p["permalink"],
                            "num_comments": p.get("num_comments", 0),
                            "upvote_ratio": p.get("upvote_ratio"),
                            "is_self": p.get("is_self", False),
                        },
                    ))
            except Exception as e:
                logger.warning("reddit_subreddit_failed", subreddit=subreddit, error=str(e))

        return items[:limit]
