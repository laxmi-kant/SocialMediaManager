"""GitHub Trending content source client."""

from app.services.content_research.base import ContentItem, ContentSourceBase

# GitHub's search API as a proxy for trending repos
SEARCH_URL = "https://api.github.com/search/repositories"


class GitHubTrendingClient(ContentSourceBase):
    source_type = "github"

    async def fetch_trending(self, limit: int = 20) -> list[ContentItem]:
        resp = await self._http_client.get(
            SEARCH_URL,
            params={"q": "created:>2026-03-13", "sort": "stars", "order": "desc", "per_page": limit},
        )
        data = resp.json()

        return [
            ContentItem(
                source_type=self.source_type,
                external_id=str(repo["id"]),
                title=repo["full_name"],
                url=repo["html_url"],
                content=repo.get("description", ""),
                author=repo.get("owner", {}).get("login"),
                score=repo.get("stargazers_count", 0),
                tags=[repo.get("language", "")] if repo.get("language") else [],
                metadata={
                    "language": repo.get("language"),
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "description": repo.get("description"),
                },
            )
            for repo in data.get("items", [])
        ]
