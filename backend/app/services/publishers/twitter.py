"""Twitter/X publisher using Twitter API v2 with OAuth 2.0 User Context."""

import structlog

from app.models.platform_account import PlatformAccount
from app.services.publishers.base import PostMetrics, PublisherBase, PublishResult
from app.utils.http_client import ResilientHTTPClient
from app.utils.security import decrypt_token

logger = structlog.get_logger()

API_URL = "https://api.twitter.com/2"
TWEET_CHAR_LIMIT = 280


class TwitterPublisher(PublisherBase):
    """Publish tweets via Twitter API v2."""

    @property
    def platform_name(self) -> str:
        return "twitter"

    def _auth_headers(self, account: PlatformAccount) -> dict:
        token = decrypt_token(account.access_token)
        return {"Authorization": f"Bearer {token}"}

    def _format_tweet(self, text: str, hashtags: list[str]) -> str:
        """Ensure tweet text + hashtags fits within char limit."""
        # Hashtags may already be in the text from AI generation
        existing_tags = {tag.lower() for tag in text.split() if tag.startswith("#")}
        new_tags = [t for t in hashtags if t.lower() not in existing_tags]

        if new_tags:
            tag_str = " " + " ".join(new_tags)
            if len(text) + len(tag_str) <= TWEET_CHAR_LIMIT:
                text = text + tag_str
        return text[:TWEET_CHAR_LIMIT]

    async def publish(self, text: str, hashtags: list[str], account: PlatformAccount) -> PublishResult:
        tweet_text = self._format_tweet(text, hashtags)
        headers = self._auth_headers(account)

        async with ResilientHTTPClient("twitter") as client:
            try:
                resp = await client.post(
                    f"{API_URL}/tweets",
                    json={"text": tweet_text},
                    headers=headers,
                )
                data = resp.json()
                tweet_id = data["data"]["id"]
                # Construct URL from account's platform_user_id
                username = account.display_name or "user"
                if username.startswith("@"):
                    username = username[1:]
                platform_url = f"https://x.com/{username}/status/{tweet_id}"

                logger.info("tweet_published", tweet_id=tweet_id)
                return PublishResult(
                    success=True,
                    platform_post_id=tweet_id,
                    platform_url=platform_url,
                )
            except Exception as exc:
                logger.error("tweet_publish_failed", error=str(exc))
                return PublishResult(success=False, error_message=str(exc))

    async def delete(self, platform_post_id: str, account: PlatformAccount) -> bool:
        headers = self._auth_headers(account)
        async with ResilientHTTPClient("twitter") as client:
            try:
                await client._request("DELETE", f"{API_URL}/tweets/{platform_post_id}", headers=headers)
                return True
            except Exception as exc:
                logger.error("tweet_delete_failed", error=str(exc))
                return False

    async def get_metrics(self, platform_post_id: str, account: PlatformAccount) -> PostMetrics:
        """Fetch tweet metrics. Note: requires Basic+ API tier."""
        headers = self._auth_headers(account)
        async with ResilientHTTPClient("twitter") as client:
            try:
                resp = await client.get(
                    f"{API_URL}/tweets/{platform_post_id}",
                    params={"tweet.fields": "public_metrics"},
                    headers=headers,
                )
                data = resp.json()
                metrics = data.get("data", {}).get("public_metrics", {})
                return PostMetrics(
                    impressions=metrics.get("impression_count", 0),
                    likes=metrics.get("like_count", 0),
                    comments=metrics.get("reply_count", 0),
                    shares=metrics.get("retweet_count", 0) + metrics.get("quote_count", 0),
                )
            except Exception as exc:
                logger.warning("tweet_metrics_failed", error=str(exc))
                return PostMetrics()
