"""Unit tests for prompt templates."""

import pytest

from app.services.ai_generator.prompts import TEMPLATES, get_prompt


class TestGetPrompt:
    def test_twitter_tech_insight(self):
        prompt = get_prompt(
            platform="twitter",
            content_type="tech_insight",
            title="AI Breakthrough",
            url="https://example.com",
            content="New AI model released",
            tone="professional",
        )
        assert "AI Breakthrough" in prompt
        assert "https://example.com" in prompt
        assert "New AI model released" in prompt
        assert "professional" in prompt

    def test_linkedin_joke(self):
        prompt = get_prompt(
            platform="linkedin",
            content_type="joke",
            content="Why do programmers prefer dark mode?",
            tone="humorous",
        )
        assert "dark mode" in prompt
        assert "humorous" in prompt

    def test_missing_fields_default_to_na(self):
        prompt = get_prompt(
            platform="twitter",
            content_type="tip",
        )
        assert "N/A" in prompt

    def test_invalid_platform_raises(self):
        with pytest.raises(ValueError, match="No template"):
            get_prompt(platform="instagram", content_type="tech_insight")

    def test_invalid_content_type_raises(self):
        with pytest.raises(ValueError, match="No template"):
            get_prompt(platform="twitter", content_type="invalid_type")

    def test_all_platforms_have_same_content_types(self):
        twitter_types = set(TEMPLATES["twitter"].keys())
        linkedin_types = set(TEMPLATES["linkedin"].keys())
        assert twitter_types == linkedin_types

    def test_github_spotlight_includes_score(self):
        prompt = get_prompt(
            platform="twitter",
            content_type="github_spotlight",
            title="awesome-project",
            content="A cool project",
            score=5000,
            url="https://github.com/user/repo",
        )
        assert "5000" in prompt
