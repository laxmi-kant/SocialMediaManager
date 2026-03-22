"""Publisher registry for managing platform publishers."""

from app.services.publishers.base import PublisherBase
from app.services.publishers.linkedin import LinkedInPublisher
from app.services.publishers.twitter import TwitterPublisher


class PublisherRegistry:
    """Registry for platform publishers - singleton pattern."""

    def __init__(self):
        self._publishers: dict[str, PublisherBase] = {}

    def register(self, publisher: PublisherBase) -> None:
        self._publishers[publisher.platform_name] = publisher

    def get(self, platform: str) -> PublisherBase:
        publisher = self._publishers.get(platform)
        if not publisher:
            raise ValueError(f"No publisher registered for platform: {platform}")
        return publisher

    def list_platforms(self) -> list[str]:
        return list(self._publishers.keys())


def get_publisher_registry() -> PublisherRegistry:
    """Create and return a configured publisher registry."""
    registry = PublisherRegistry()
    registry.register(TwitterPublisher())
    registry.register(LinkedInPublisher())
    return registry


# Global singleton
publisher_registry = get_publisher_registry()
