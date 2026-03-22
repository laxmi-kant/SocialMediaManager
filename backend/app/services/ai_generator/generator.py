"""Post generation service - generates social media posts from content sources."""

import re
import uuid

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_source import ContentSource
from app.models.generated_post import GeneratedPost
from app.services.ai_generator.client import AnthropicClientWrapper
from app.services.ai_generator.prompts import SYSTEM_PROMPT, get_prompt

logger = structlog.get_logger()

TWITTER_CHAR_LIMIT = 280
LINKEDIN_CHAR_LIMIT = 3000


class PostGenerator:
    """Generates social media posts using Claude AI."""

    def __init__(self, db: AsyncSession, ai_client: AnthropicClientWrapper | None = None):
        self.db = db
        self.ai_client = ai_client or AnthropicClientWrapper()

    async def generate_post(
        self,
        content_source_id: uuid.UUID,
        target_platform: str,
        content_type: str,
        tone: str,
        user_id: uuid.UUID,
    ) -> GeneratedPost:
        # Load content source
        result = await self.db.execute(select(ContentSource).where(ContentSource.id == content_source_id))
        source = result.scalar_one_or_none()
        if not source:
            raise ValueError("Content source not found")

        # Build prompt
        prompt = get_prompt(
            platform=target_platform,
            content_type=content_type,
            title=source.title,
            url=source.url or "",
            content=source.content or "",
            score=source.score,
            tone=tone,
        )

        # Generate with AI
        gen_result = self.ai_client.generate(prompt=prompt, system=SYSTEM_PROMPT)

        # Post-process
        text = gen_result.text.strip()
        text = self._validate_platform_limits(text, target_platform)
        hashtags = self._extract_hashtags(text)

        # Save as draft
        post = GeneratedPost(
            user_id=user_id,
            content_source_id=content_source_id,
            target_platform=target_platform,
            content_text=text,
            content_type=content_type,
            tone=tone,
            hashtags=hashtags,
            ai_model=gen_result.model,
            prompt_used=prompt,
            token_usage={"input_tokens": gen_result.input_tokens, "output_tokens": gen_result.output_tokens},
            status="draft",
        )
        self.db.add(post)
        await self.db.flush()
        await self.db.refresh(post)

        logger.info("post_generated", post_id=str(post.id), platform=target_platform, content_type=content_type)
        return post

    async def regenerate_post(self, post_id: uuid.UUID, user_id: uuid.UUID) -> GeneratedPost:
        """Regenerate an existing post."""
        result = await self.db.execute(
            select(GeneratedPost).where(GeneratedPost.id == post_id, GeneratedPost.user_id == user_id)
        )
        post = result.scalar_one_or_none()
        if not post:
            raise ValueError("Post not found")
        if not post.content_source_id:
            raise ValueError("Post has no content source to regenerate from")

        return await self.generate_post(
            content_source_id=post.content_source_id,
            target_platform=post.target_platform,
            content_type=post.content_type,
            tone=post.tone,
            user_id=user_id,
        )

    def _validate_platform_limits(self, text: str, platform: str) -> str:
        limit = TWITTER_CHAR_LIMIT if platform == "twitter" else LINKEDIN_CHAR_LIMIT
        if len(text) > limit:
            # Truncate at last space before limit, add ellipsis
            text = text[: limit - 1].rsplit(" ", 1)[0] + "…"
        return text

    def _extract_hashtags(self, text: str) -> list[str]:
        return re.findall(r"#\w+", text)
