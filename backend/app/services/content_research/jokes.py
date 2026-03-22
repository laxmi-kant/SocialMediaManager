"""Joke content source client (JokeAPI + icanhazdadjoke)."""

import structlog

from app.services.content_research.base import ContentItem, ContentSourceBase
from app.utils.http_client import ResilientHTTPClient

logger = structlog.get_logger()

JOKEAPI_URL = "https://v2.jokeapi.dev/joke/Any"
DADJOKE_URL = "https://icanhazdadjoke.com/"


class JokeClient(ContentSourceBase):
    source_type = "joke"

    def __init__(self):
        super().__init__()
        self._dadjoke_client = ResilientHTTPClient(
            service_name="jokeapi", headers={"Accept": "application/json"}
        )

    async def fetch_trending(self, limit: int = 10) -> list[ContentItem]:
        items: list[ContentItem] = []

        # JokeAPI batch
        joke_count = max(1, limit // 2)
        try:
            resp = await self._http_client.get(
                JOKEAPI_URL, params={"amount": joke_count, "type": "twopart,single", "safe-mode": ""}
            )
            data = resp.json()
            jokes = data.get("jokes", [data] if "joke" in data or "setup" in data else [])
            for j in jokes:
                if j.get("type") == "twopart":
                    text = f"{j['setup']}\n\n{j['delivery']}"
                    title = j["setup"]
                else:
                    text = j.get("joke", "")
                    title = text[:80]

                items.append(ContentItem(
                    source_type=self.source_type,
                    external_id=f"jokeapi-{j.get('id', len(items))}",
                    title=title,
                    content=text,
                    score=0,
                    tags=[j.get("category", "General")],
                    metadata={"source": "jokeapi", "category": j.get("category"), "type": j.get("type"), "safe": j.get("safe", True)},
                ))
        except Exception as e:
            logger.warning("jokeapi_fetch_failed", error=str(e))

        # icanhazdadjoke
        dadjoke_count = limit - len(items)
        for i in range(dadjoke_count):
            try:
                resp = await self._dadjoke_client.get(DADJOKE_URL)
                data = resp.json()
                items.append(ContentItem(
                    source_type=self.source_type,
                    external_id=f"dadjoke-{data.get('id', i)}",
                    title=data.get("joke", "")[:80],
                    content=data.get("joke", ""),
                    score=0,
                    tags=["Dad Joke"],
                    metadata={"source": "icanhazdadjoke"},
                ))
            except Exception as e:
                logger.warning("dadjoke_fetch_failed", error=str(e))
                break

        return items

    async def close(self):
        await super().close()
        await self._dadjoke_client.close()
