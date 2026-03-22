"""Integration tests for content API endpoints."""

import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_source import ContentSource
from app.models.user import User
from app.utils.security import create_access_token


@pytest.fixture
def auth_cookies(test_user: User) -> dict:
    token = create_access_token(test_user.id)
    return {"access_token": token}


@pytest_asyncio.fixture
async def sample_content(db_session: AsyncSession):
    items = []
    for i in range(3):
        cs = ContentSource(
            source_type="hackernews",
            external_id=f"hn-{i}",
            title=f"Test Story {i}",
            url=f"https://example.com/{i}",
            score=100 - i * 10,
        )
        db_session.add(cs)
        items.append(cs)
    await db_session.commit()
    for item in items:
        await db_session.refresh(item)
    return items


@pytest.mark.asyncio
class TestListContent:
    async def test_list_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/v1/content")
        assert resp.status_code == 401

    async def test_list_returns_content(self, client: AsyncClient, auth_cookies, sample_content):
        resp = await client.get("/api/v1/content", cookies=auth_cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    async def test_list_filter_by_source(self, client: AsyncClient, auth_cookies, sample_content):
        resp = await client.get("/api/v1/content", params={"source_type": "reddit"}, cookies=auth_cookies)
        assert resp.status_code == 200
        assert resp.json()["total"] == 0


@pytest.mark.asyncio
class TestGetContent:
    async def test_get_by_id(self, client: AsyncClient, auth_cookies, sample_content):
        item_id = str(sample_content[0].id)
        resp = await client.get(f"/api/v1/content/{item_id}", cookies=auth_cookies)
        assert resp.status_code == 200
        assert resp.json()["title"] == "Test Story 0"

    async def test_get_not_found(self, client: AsyncClient, auth_cookies):
        resp = await client.get(f"/api/v1/content/{uuid.uuid4()}", cookies=auth_cookies)
        assert resp.status_code == 404
