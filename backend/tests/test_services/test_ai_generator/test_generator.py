"""Unit tests for PostGenerator service."""

import uuid
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_source import ContentSource
from app.models.generated_post import GeneratedPost
from app.services.ai_generator.client import GenerationResult
from app.services.ai_generator.generator import PostGenerator


@pytest_asyncio.fixture
async def content_source(db_session: AsyncSession):
    cs = ContentSource(
        source_type="hackernews",
        external_id="hn-gen-1",
        title="AI Models Getting Better",
        url="https://example.com/ai",
        content="New research shows significant improvements in AI capabilities.",
        score=200,
    )
    db_session.add(cs)
    await db_session.commit()
    await db_session.refresh(cs)
    return cs


@pytest.mark.asyncio
class TestPostGenerator:
    async def test_generate_post_creates_draft(self, db_session: AsyncSession, content_source, test_user):
        mock_ai = MagicMock()
        mock_ai.generate.return_value = GenerationResult(
            text="AI is evolving fast! Check out the latest breakthroughs #AI #Tech",
            model="claude-haiku-4-5-20251001",
            input_tokens=100,
            output_tokens=50,
        )

        generator = PostGenerator(db=db_session, ai_client=mock_ai)
        post = await generator.generate_post(
            content_source_id=content_source.id,
            target_platform="twitter",
            content_type="tech_insight",
            tone="professional",
            user_id=test_user.id,
        )

        assert isinstance(post, GeneratedPost)
        assert post.status == "draft"
        assert post.target_platform == "twitter"
        assert post.content_type == "tech_insight"
        assert post.tone == "professional"
        assert post.user_id == test_user.id
        assert post.content_source_id == content_source.id
        assert post.ai_model == "claude-haiku-4-5-20251001"
        assert "#AI" in post.hashtags
        assert "#Tech" in post.hashtags
        assert post.token_usage == {"input_tokens": 100, "output_tokens": 50}
        mock_ai.generate.assert_called_once()

    async def test_generate_post_missing_source_raises(self, db_session: AsyncSession, test_user):
        mock_ai = MagicMock()
        generator = PostGenerator(db=db_session, ai_client=mock_ai)

        with pytest.raises(ValueError, match="Content source not found"):
            await generator.generate_post(
                content_source_id=uuid.uuid4(),
                target_platform="twitter",
                content_type="tech_insight",
                tone="professional",
                user_id=test_user.id,
            )

    async def test_generate_post_truncates_long_twitter(self, db_session: AsyncSession, content_source, test_user):
        long_text = "A" * 300 + " #Tech"
        mock_ai = MagicMock()
        mock_ai.generate.return_value = GenerationResult(
            text=long_text, model="test", input_tokens=10, output_tokens=10,
        )

        generator = PostGenerator(db=db_session, ai_client=mock_ai)
        post = await generator.generate_post(
            content_source_id=content_source.id,
            target_platform="twitter",
            content_type="tech_insight",
            tone="professional",
            user_id=test_user.id,
        )

        assert len(post.content_text) <= 280

    async def test_generate_post_linkedin_no_truncation(self, db_session: AsyncSession, content_source, test_user):
        text = "A great post about AI. " * 20 + "#AI #Tech"
        mock_ai = MagicMock()
        mock_ai.generate.return_value = GenerationResult(
            text=text, model="test", input_tokens=10, output_tokens=10,
        )

        generator = PostGenerator(db=db_session, ai_client=mock_ai)
        post = await generator.generate_post(
            content_source_id=content_source.id,
            target_platform="linkedin",
            content_type="tech_insight",
            tone="professional",
            user_id=test_user.id,
        )

        # Should not truncate since it's well under 3000 chars
        assert "#AI" in post.content_text

    async def test_extract_hashtags(self, db_session: AsyncSession):
        mock_ai = MagicMock()
        generator = PostGenerator(db=db_session, ai_client=mock_ai)

        tags = generator._extract_hashtags("Hello #World #Python #AI no hashtag here")
        assert tags == ["#World", "#Python", "#AI"]

    async def test_extract_hashtags_empty(self, db_session: AsyncSession):
        mock_ai = MagicMock()
        generator = PostGenerator(db=db_session, ai_client=mock_ai)

        tags = generator._extract_hashtags("No hashtags in this text")
        assert tags == []

    async def test_validate_platform_limits_twitter(self, db_session: AsyncSession):
        mock_ai = MagicMock()
        generator = PostGenerator(db=db_session, ai_client=mock_ai)

        short = generator._validate_platform_limits("Short text", "twitter")
        assert short == "Short text"

        long = generator._validate_platform_limits("A " * 200, "twitter")
        assert len(long) <= 280

    async def test_validate_platform_limits_linkedin(self, db_session: AsyncSession):
        mock_ai = MagicMock()
        generator = PostGenerator(db=db_session, ai_client=mock_ai)

        text = "A " * 1600  # 3200 chars
        result = generator._validate_platform_limits(text, "linkedin")
        assert len(result) <= 3000
