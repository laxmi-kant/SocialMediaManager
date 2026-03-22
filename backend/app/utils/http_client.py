"""Resilient async HTTP client with retry and exponential backoff."""

import asyncio
from dataclasses import dataclass, field

import httpx
import structlog

logger = structlog.get_logger()


@dataclass
class RetryPolicy:
    max_retries: int = 3
    backoff: float = 1.0
    retry_on: list[int] = field(default_factory=lambda: [429, 500, 502, 503])


# Default retry policies per service (from LLD)
RETRY_POLICIES: dict[str, RetryPolicy] = {
    "hackernews": RetryPolicy(max_retries=3, backoff=1.0, retry_on=[429, 500, 502, 503]),
    "reddit": RetryPolicy(max_retries=3, backoff=2.0, retry_on=[429, 500, 502, 503]),
    "devto": RetryPolicy(max_retries=2, backoff=1.0, retry_on=[429, 500, 502, 503]),
    "jokeapi": RetryPolicy(max_retries=2, backoff=0.5, retry_on=[429, 500]),
    "github": RetryPolicy(max_retries=2, backoff=1.0, retry_on=[429, 500, 502]),
    "claude": RetryPolicy(max_retries=3, backoff=2.0, retry_on=[429, 500, 529]),
    "twitter": RetryPolicy(max_retries=2, backoff=5.0, retry_on=[429, 500, 503]),
    "linkedin": RetryPolicy(max_retries=2, backoff=5.0, retry_on=[429, 500, 503]),
}


class ResilientHTTPClient:
    """Async HTTP client with automatic retry and exponential backoff."""

    def __init__(self, service_name: str, timeout: float = 30.0, headers: dict | None = None):
        self.service_name = service_name
        self.policy = RETRY_POLICIES.get(service_name, RetryPolicy())
        self._client = httpx.AsyncClient(timeout=timeout, headers=headers or {})

    async def get(self, url: str, **kwargs) -> httpx.Response:
        return await self._request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        return await self._request("POST", url, **kwargs)

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        last_exc = None
        for attempt in range(self.policy.max_retries + 1):
            try:
                response = await self._client.request(method, url, **kwargs)
                if response.status_code in self.policy.retry_on and attempt < self.policy.max_retries:
                    wait = self.policy.backoff * (2 ** attempt)
                    logger.warning(
                        "retryable_status",
                        service=self.service_name,
                        status=response.status_code,
                        attempt=attempt + 1,
                        wait=wait,
                    )
                    await asyncio.sleep(wait)
                    continue
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError:
                raise
            except httpx.HTTPError as exc:
                last_exc = exc
                if attempt < self.policy.max_retries:
                    wait = self.policy.backoff * (2 ** attempt)
                    logger.warning(
                        "request_error_retry",
                        service=self.service_name,
                        error=str(exc),
                        attempt=attempt + 1,
                        wait=wait,
                    )
                    await asyncio.sleep(wait)
                else:
                    logger.error("request_failed", service=self.service_name, error=str(exc))
                    raise

        raise last_exc  # type: ignore[misc]

    async def close(self):
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
