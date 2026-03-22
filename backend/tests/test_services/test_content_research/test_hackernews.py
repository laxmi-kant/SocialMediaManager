"""Unit tests for HackerNews client."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.content_research.hackernews import HackerNewsClient


@pytest.mark.asyncio
class TestHackerNewsClient:
    async def test_fetch_trending(self):
        client = HackerNewsClient()

        mock_response_ids = AsyncMock()
        mock_response_ids.json.return_value = [1, 2, 3]

        mock_story = AsyncMock()
        mock_story.json.return_value = {
            "id": 1,
            "title": "Test Story",
            "url": "https://example.com",
            "by": "testuser",
            "score": 100,
            "descendants": 50,
            "type": "story",
        }

        with patch.object(client._http_client, "get", side_effect=[mock_response_ids, mock_story, mock_story, mock_story]):
            items = await client.fetch_trending(limit=3)

        assert len(items) == 3
        assert items[0].source_type == "hackernews"
        assert items[0].title == "Test Story"
        assert items[0].score == 100

        await client.close()
