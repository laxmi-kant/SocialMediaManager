"""Unit tests for RedisRateLimiter."""

from unittest.mock import AsyncMock

import pytest

from app.utils.rate_limiter import RedisRateLimiter


@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    pipe = AsyncMock()
    redis.pipeline.return_value = pipe
    return redis, pipe


@pytest.fixture
def limiter(mock_redis):
    redis, _ = mock_redis
    return RedisRateLimiter(redis)


@pytest.mark.asyncio
class TestRedisRateLimiter:
    async def test_is_allowed_under_limit(self, limiter, mock_redis):
        _, pipe = mock_redis
        pipe.execute.return_value = [None, 5, None, None]  # zremrange, zcard=5, zadd, expire
        result = await limiter.is_allowed("ratelimit:test", max_requests=10, window_seconds=60)
        assert result is True

    async def test_is_denied_over_limit(self, limiter, mock_redis):
        _, pipe = mock_redis
        pipe.execute.return_value = [None, 10, None, None]  # zcard=10 (at limit)
        result = await limiter.is_allowed("ratelimit:test", max_requests=10, window_seconds=60)
        assert result is False

    async def test_get_remaining(self, limiter, mock_redis):
        redis, _ = mock_redis
        redis.zremrangebyscore.return_value = None
        redis.zcard.return_value = 7
        remaining = await limiter.get_remaining("ratelimit:test", max_requests=10, window_seconds=60)
        assert remaining == 3
