"""LinkedIn publisher using LinkedIn Marketing API with OAuth 2.0."""

import structlog

from app.models.platform_account import PlatformAccount
from app.services.publishers.base import PostMetrics, PublisherBase, PublishResult
from app.utils.http_client import ResilientHTTPClient
from app.utils.security import decrypt_token

logger = structlog.get_logger()

API_URL = "https://api.linkedin.com/rest"
LINKEDIN_CHAR_LIMIT = 3000


class LinkedInPublisher(PublisherBase):
    """Publish posts via LinkedIn API."""

    @property
    def platform_name(self) -> str:
        return "linkedin"

    def _auth_headers(self, account: PlatformAccount) -> dict:
        token = decrypt_token(account.access_token)
        return {
            "Authorization": f"Bearer {token}",
            "LinkedIn-Version": "202402",
            "X-Restli-Protocol-Version": "2.0.0",
        }

    def _format_post(self, text: str, hashtags: list[str]) -> str:
        """Add any missing hashtags to the post text."""
        existing_tags = {tag.lower() for tag in text.split() if tag.startswith("#")}
        new_tags = [t for t in hashtags if t.lower() not in existing_tags]

        if new_tags:
            tag_str = "\n\n" + " ".join(new_tags)
            if len(text) + len(tag_str) <= LINKEDIN_CHAR_LIMIT:
                text = text + tag_str
        return text[:LINKEDIN_CHAR_LIMIT]

    async def publish(self, text: str, hashtags: list[str], account: PlatformAccount) -> PublishResult:
        post_text = self._format_post(text, hashtags)
        headers = self._auth_headers(account)

        # LinkedIn requires the author URN
        author_urn = f"urn:li:person:{account.platform_user_id}"

        payload = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": post_text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }

        async with ResilientHTTPClient("linkedin") as client:
            try:
                resp = await client.post(
                    f"{API_URL}/posts",
                    json=payload,
                    headers=headers,
                )
                # LinkedIn returns post URN in the x-restli-id header or response body
                post_urn = resp.headers.get("x-restli-id", "")
                if not post_urn and resp.status_code == 201:
                    data = resp.json()
                    post_urn = data.get("id", "")

                platform_url = ""
                if post_urn:
                    # Extract activity ID from URN for URL
                    activity_id = post_urn.split(":")[-1] if ":" in post_urn else post_urn
                    platform_url = f"https://www.linkedin.com/feed/update/{post_urn}"

                logger.info("linkedin_post_published", post_urn=post_urn)
                return PublishResult(
                    success=True,
                    platform_post_id=post_urn,
                    platform_url=platform_url,
                )
            except Exception as exc:
                logger.error("linkedin_publish_failed", error=str(exc))
                return PublishResult(success=False, error_message=str(exc))

    async def delete(self, platform_post_id: str, account: PlatformAccount) -> bool:
        headers = self._auth_headers(account)
        async with ResilientHTTPClient("linkedin") as client:
            try:
                await client._request("DELETE", f"{API_URL}/posts/{platform_post_id}", headers=headers)
                return True
            except Exception as exc:
                logger.error("linkedin_delete_failed", error=str(exc))
                return False

    async def get_metrics(self, platform_post_id: str, account: PlatformAccount) -> PostMetrics:
        """Fetch LinkedIn post metrics."""
        headers = self._auth_headers(account)
        async with ResilientHTTPClient("linkedin") as client:
            try:
                resp = await client.get(
                    f"{API_URL}/socialActions/{platform_post_id}",
                    headers=headers,
                )
                data = resp.json()
                return PostMetrics(
                    likes=data.get("likesSummary", {}).get("totalLikes", 0),
                    comments=data.get("commentsSummary", {}).get("totalFirstLevelComments", 0),
                    shares=data.get("sharesSummary", {}).get("totalShares", 0),
                )
            except Exception as exc:
                logger.warning("linkedin_metrics_failed", error=str(exc))
                return PostMetrics()
