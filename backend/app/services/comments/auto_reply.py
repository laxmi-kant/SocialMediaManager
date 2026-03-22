"""Auto-reply processor for comments."""

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.comment import Comment, CommentReply
from app.models.generated_post import GeneratedPost
from app.models.platform_account import PlatformAccount
from app.models.published_post import PublishedPost
from app.services.comments.classifier import CommentClassifier
from app.services.comments.reply_generator import CommentReplyGenerator
from app.utils.http_client import ResilientHTTPClient
from app.utils.security import decrypt_token

logger = structlog.get_logger()


class AutoReplyProcessor:
    """Processes comments for auto-reply: classify, generate reply, optionally send."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.classifier = CommentClassifier()
        self.reply_generator = CommentReplyGenerator()

    async def process_comment(self, comment: Comment, auto_send: bool = False) -> CommentReply | None:
        """Classify a comment, generate a reply, and optionally send it."""
        # Skip spam
        if comment.sentiment == "spam" or comment.comment_type == "spam":
            return None

        # Classify if not already done
        if not comment.sentiment:
            sentiment, comment_type = self.classifier.classify(comment)
            comment.sentiment = sentiment
            comment.comment_type = comment_type
            await self.db.flush()

        # Skip spam after classification
        if comment.comment_type == "spam":
            return None

        # Get the original post text for context
        pub_post = await self.db.get(PublishedPost, comment.published_post_id)
        if not pub_post:
            return None

        gen_post = await self.db.get(GeneratedPost, pub_post.generated_post_id)
        post_text = gen_post.content_text if gen_post else ""

        # Generate reply
        reply = self.reply_generator.generate_reply(comment, post_text)
        self.db.add(reply)
        await self.db.flush()
        await self.db.refresh(reply)

        # Auto-send if enabled
        if auto_send:
            await self._send_reply(reply, comment, pub_post)

        return reply

    async def _send_reply(self, reply: CommentReply, comment: Comment, pub_post: PublishedPost) -> None:
        """Send a reply to the platform."""
        # Get platform account
        result = await self.db.execute(
            select(PlatformAccount).where(PlatformAccount.id == pub_post.platform_account_id)
        )
        account = result.scalar_one_or_none()
        if not account:
            reply.status = "failed"
            reply.error_message = "No platform account found"
            return

        try:
            token = decrypt_token(account.access_token)
            headers = {
                "Authorization": f"Bearer {token}",
                "LinkedIn-Version": "202402",
                "X-Restli-Protocol-Version": "2.0.0",
            }

            async with ResilientHTTPClient("linkedin") as client:
                resp = await client.post(
                    f"https://api.linkedin.com/rest/socialActions/{pub_post.platform_post_id}/comments",
                    json={
                        "actor": f"urn:li:person:{account.platform_user_id}",
                        "message": {"text": reply.reply_text},
                    },
                    headers=headers,
                )
                reply_id = resp.headers.get("x-restli-id", "")
                reply.platform_reply_id = reply_id
                reply.status = "sent"
                reply.reply_mode = "auto"
                from datetime import datetime, timezone
                reply.sent_at = datetime.now(timezone.utc)
                logger.info("auto_reply_sent", comment_id=str(comment.id))

        except Exception as exc:
            reply.status = "failed"
            reply.error_message = str(exc)
            logger.error("auto_reply_failed", comment_id=str(comment.id), error=str(exc))
