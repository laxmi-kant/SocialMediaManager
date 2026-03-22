"""Fetch comments from LinkedIn posts via API."""

from datetime import datetime, timezone

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.models.platform_account import PlatformAccount
from app.models.published_post import PublishedPost
from app.utils.http_client import ResilientHTTPClient
from app.utils.security import decrypt_token

logger = structlog.get_logger()

API_URL = "https://api.linkedin.com/rest"


class CommentFetcher:
    """Fetches comments from LinkedIn published posts."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def fetch_comments_for_post(self, published_post: PublishedPost, account: PlatformAccount) -> list[Comment]:
        """Fetch comments for a single published post."""
        if not published_post.platform_post_id:
            return []

        token = decrypt_token(account.access_token)
        headers = {
            "Authorization": f"Bearer {token}",
            "LinkedIn-Version": "202402",
            "X-Restli-Protocol-Version": "2.0.0",
        }

        comments = []
        async with ResilientHTTPClient("linkedin") as client:
            try:
                resp = await client.get(
                    f"{API_URL}/socialActions/{published_post.platform_post_id}/comments",
                    headers=headers,
                    params={"count": 50},
                )
                data = resp.json()
                elements = data.get("elements", [])

                for elem in elements:
                    comment_id = elem.get("$URN", elem.get("id", ""))
                    text = elem.get("message", {}).get("text", "")
                    actor = elem.get("actor~", {})

                    # Check if already exists
                    existing = await self.db.execute(
                        select(Comment).where(
                            Comment.platform == "linkedin",
                            Comment.platform_comment_id == str(comment_id),
                        )
                    )
                    if existing.scalar_one_or_none():
                        continue

                    comment = Comment(
                        published_post_id=published_post.id,
                        platform="linkedin",
                        platform_comment_id=str(comment_id),
                        commenter_name=actor.get("localizedFirstName", "") + " " + actor.get("localizedLastName", ""),
                        commenter_profile_url=f"https://www.linkedin.com/in/{actor.get('vanityName', '')}",
                        comment_text=text,
                        commented_at=datetime.now(timezone.utc),
                    )
                    self.db.add(comment)
                    comments.append(comment)

                if comments:
                    await self.db.flush()
                    logger.info("comments_fetched", post_id=str(published_post.id), count=len(comments))

            except Exception as exc:
                logger.error("comment_fetch_error", post_id=str(published_post.id), error=str(exc))

        return comments
