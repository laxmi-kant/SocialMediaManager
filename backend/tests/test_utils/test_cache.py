"""Unit tests for RedisCache helper."""

from unittest.mock import AsyncMock

import pytest

from app.utils.cache import RedisCache


@pytest.fixture
def mock_redis():
    return AsyncMock()


@pytest.fixture
def cache(mock_redis):
    return RedisCache(mock_redis)


@pytest.mark.asyncio
class TestRedisCache:
    async def test_get_returns_parsed_json(self, cache, mock_redis):
        mock_redis.get.return_value = '{"key": "value"}'
        result = await cache.get("test:key")
        assert result == {"key": "value"}
        mock_redis.get.assert_called_once_with("test:key")

    async def test_get_returns_none_on_miss(self, cache, mock_redis):
        mock_redis.get.return_value = None
        result = await cache.get("test:missing")
        assert result is None

    async def test_set_stores_json_with_ttl(self, cache, mock_redis):
        await cache.set("test:key", {"data": 1}, ttl=600)
        mock_redis.set.assert_called_once()
        args = mock_redis.set.call_args
        assert args[0][0] == "test:key"
        assert args[1]["ex"] == 600

    async def test_delete(self, cache, mock_redis):
        await cache.delete("test:key")
        mock_redis.delete.assert_called_once_with("test:key")

    async def test_exists(self, cache, mock_redis):
        mock_redis.exists.return_value = 1
        result = await cache.exists("test:key")
        assert result is True
