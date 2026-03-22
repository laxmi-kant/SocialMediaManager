"""Abstract base class for social media publishers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.models.platform_account import PlatformAccount


@dataclass
class PublishResult:
    success: bool
    platform_post_id: str | None = None
    platform_url: str | None = None
    error_message: str | None = None


@dataclass
class PostMetrics:
    impressions: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    clicks: int = 0


class PublisherBase(ABC):
    """Abstract base class for platform publishers."""

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Return the platform identifier (e.g., 'twitter', 'linkedin')."""

    @abstractmethod
    async def publish(self, text: str, hashtags: list[str], account: PlatformAccount) -> PublishResult:
        """Publish a post to the platform."""

    @abstractmethod
    async def delete(self, platform_post_id: str, account: PlatformAccount) -> bool:
        """Delete a post from the platform."""

    @abstractmethod
    async def get_metrics(self, platform_post_id: str, account: PlatformAccount) -> PostMetrics:
        """Fetch engagement metrics for a post."""
