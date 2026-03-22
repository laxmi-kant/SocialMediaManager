"""Unit tests for PublisherRegistry."""

import pytest

from app.services.publishers.base import PublisherBase
from app.services.publishers.registry import PublisherRegistry, get_publisher_registry


class TestPublisherRegistry:
    def test_default_registry_has_both_platforms(self):
        registry = get_publisher_registry()
        platforms = registry.list_platforms()
        assert "twitter" in platforms
        assert "linkedin" in platforms

    def test_get_registered_publisher(self):
        registry = get_publisher_registry()
        twitter = registry.get("twitter")
        assert twitter.platform_name == "twitter"

        linkedin = registry.get("linkedin")
        assert linkedin.platform_name == "linkedin"

    def test_get_unregistered_platform_raises(self):
        registry = PublisherRegistry()
        with pytest.raises(ValueError, match="No publisher registered"):
            registry.get("instagram")

    def test_list_platforms_empty(self):
        registry = PublisherRegistry()
        assert registry.list_platforms() == []
