"""Abstract base class for content source clients."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

from app.utils.http_client import ResilientHTTPClient


@dataclass
class ContentItem:
    """Standardized content item from any source."""

    source_type: str
    external_id: str
    title: str
    url: str | None = None
    content: str | None = None
    author: str | None = None
    score: int = 0
    tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    fetched_at: datetime = field(default_factory=datetime.utcnow)


class ContentSourceBase(ABC):
    """Base class for all content source clients."""

    def __init__(self):
        self._http_client = ResilientHTTPClient(service_name=self.source_type)

    @property
    @abstractmethod
    def source_type(self) -> str:
        """Unique identifier for this source (e.g., 'hackernews', 'reddit')."""

    @abstractmethod
    async def fetch_trending(self, limit: int = 20) -> list[ContentItem]:
        """Fetch trending content items from this source."""

    async def close(self):
        await self._http_client.close()
