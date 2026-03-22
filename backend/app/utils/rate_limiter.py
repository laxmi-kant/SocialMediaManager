"""Sliding window rate limiter backed by Redis."""

import time

import redis.asyncio as aioredis


class RedisRateLimiter:
    """Sliding window rate limiter using Redis sorted sets."""

    def __init__(self, redis_client: aioredis.Redis):
        self._redis = redis_client

    async def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Check if a request is allowed under the rate limit."""
        now = time.time()
        window_start = now - window_seconds
        pipe = self._redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        pipe.zadd(key, {str(now): now})
        pipe.expire(key, window_seconds)
        results = await pipe.execute()
        current_count = results[1]
        return current_count < max_requests

    async def get_remaining(self, key: str, max_requests: int, window_seconds: int) -> int:
        """Get remaining requests in the current window."""
        now = time.time()
        window_start = now - window_seconds
        await self._redis.zremrangebyscore(key, 0, window_start)
        current_count = await self._redis.zcard(key)
        return max(0, max_requests - current_count)
