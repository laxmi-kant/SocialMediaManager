"""AI-powered comment reply generation."""

import structlog

from app.models.comment import Comment, CommentReply
from app.services.ai_generator.client import AnthropicClientWrapper

logger = structlog.get_logger()

REPLY_PROMPT = """Generate a reply to this social media comment. The reply should be:
- Tone: {tone}
- Professional and contextual
- Concise (1-3 sentences)
- Natural sounding

Original post context: {post_text}
Comment by {commenter}: {comment_text}
Comment sentiment: {sentiment}
Comment type: {comment_type}

Write only the reply text, no explanations."""


class CommentReplyGenerator:
    """Generates AI-powered replies to comments."""

    def __init__(self, ai_client: AnthropicClientWrapper | None = None):
        self.ai_client = ai_client or AnthropicClientWrapper()

    def generate_reply(
        self,
        comment: Comment,
        post_text: str,
        tone: str = "professional",
    ) -> CommentReply:
        """Generate an AI reply for a comment."""
        prompt = REPLY_PROMPT.format(
            tone=tone,
            post_text=post_text[:300],
            commenter=comment.commenter_name or "Anonymous",
            comment_text=comment.comment_text[:500],
            sentiment=comment.sentiment or "neutral",
            comment_type=comment.comment_type or "other",
        )

        result = self.ai_client.generate(prompt=prompt, max_tokens=256)

        reply = CommentReply(
            comment_id=comment.id,
            reply_text=result.text.strip(),
            ai_suggested_text=result.text.strip(),
            ai_model=result.model,
            token_usage={"input_tokens": result.input_tokens, "output_tokens": result.output_tokens},
            reply_mode="ai_suggested",
            status="draft",
        )

        logger.info("reply_generated", comment_id=str(comment.id))
        return reply
