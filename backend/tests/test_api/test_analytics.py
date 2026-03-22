"""Integration tests for analytics and dashboard API endpoints."""

import pytest
from httpx import AsyncClient

from app.models.user import User
from app.utils.security import create_access_token


@pytest.fixture
def auth_cookies(test_user: User) -> dict:
    token = create_access_token(test_user.id)
    return {"access_token": token}


@pytest.mark.asyncio
class TestAnalytics:
    async def test_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/v1/analytics")
        assert resp.status_code == 401

    async def test_empty_analytics(self, client: AsyncClient, auth_cookies):
        resp = await client.get("/api/v1/analytics", cookies=auth_cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_posts"] == 0
        assert data["total_impressions"] == 0
        assert data["avg_engagement_rate"] == 0.0
        assert data["posts"] == []

    async def test_filter_by_days(self, client: AsyncClient, auth_cookies):
        resp = await client.get("/api/v1/analytics", params={"days": 7}, cookies=auth_cookies)
        assert resp.status_code == 200

    async def test_filter_by_platform(self, client: AsyncClient, auth_cookies):
        resp = await client.get("/api/v1/analytics", params={"platform": "twitter"}, cookies=auth_cookies)
        assert resp.status_code == 200


@pytest.mark.asyncio
class TestDashboard:
    async def test_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/v1/dashboard")
        assert resp.status_code == 401

    async def test_empty_dashboard(self, client: AsyncClient, auth_cookies):
        resp = await client.get("/api/v1/dashboard", cookies=auth_cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_posts"] == 0
        assert data["published_posts"] == 0
        assert data["scheduled_posts"] == 0
        assert data["draft_posts"] == 0
        assert data["recent_posts"] == []
        assert data["upcoming_posts"] == []
