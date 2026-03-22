"""Integration tests for schedule API endpoints."""

import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schedule import Schedule
from app.models.user import User
from app.utils.security import create_access_token


@pytest.fixture
def auth_cookies(test_user: User) -> dict:
    token = create_access_token(test_user.id)
    return {"access_token": token}


@pytest_asyncio.fixture
async def sample_schedule(db_session: AsyncSession, test_user: User) -> Schedule:
    schedule = Schedule(
        user_id=test_user.id,
        name="Morning Tech Posts",
        platform="twitter",
        content_types=["tech_insight", "tip"],
        cron_expression="0 9 * * 1-5",
        timezone="UTC",
        auto_approve=False,
        is_active=True,
    )
    db_session.add(schedule)
    await db_session.commit()
    await db_session.refresh(schedule)
    return schedule


@pytest.mark.asyncio
class TestListSchedules:
    async def test_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/v1/schedules")
        assert resp.status_code == 401

    async def test_list_empty(self, client: AsyncClient, auth_cookies):
        resp = await client.get("/api/v1/schedules", cookies=auth_cookies)
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    async def test_list_with_schedules(self, client: AsyncClient, auth_cookies, sample_schedule):
        resp = await client.get("/api/v1/schedules", cookies=auth_cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "Morning Tech Posts"


@pytest.mark.asyncio
class TestCreateSchedule:
    async def test_create(self, client: AsyncClient, auth_cookies):
        resp = await client.post(
            "/api/v1/schedules",
            json={
                "name": "LinkedIn Daily",
                "platform": "linkedin",
                "content_types": ["news_commentary"],
                "cron_expression": "0 12 * * *",
            },
            cookies=auth_cookies,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "LinkedIn Daily"
        assert data["platform"] == "linkedin"
        assert data["is_active"] is True

    async def test_create_invalid_platform(self, client: AsyncClient, auth_cookies):
        resp = await client.post(
            "/api/v1/schedules",
            json={
                "name": "Bad",
                "platform": "instagram",
                "content_types": ["tip"],
                "cron_expression": "0 9 * * *",
            },
            cookies=auth_cookies,
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestUpdateSchedule:
    async def test_update_name(self, client: AsyncClient, auth_cookies, sample_schedule):
        resp = await client.put(
            f"/api/v1/schedules/{sample_schedule.id}",
            json={"name": "Updated Name"},
            cookies=auth_cookies,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Name"

    async def test_toggle_active(self, client: AsyncClient, auth_cookies, sample_schedule):
        resp = await client.put(
            f"/api/v1/schedules/{sample_schedule.id}",
            json={"is_active": False},
            cookies=auth_cookies,
        )
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False


@pytest.mark.asyncio
class TestDeleteSchedule:
    async def test_delete(self, client: AsyncClient, auth_cookies, sample_schedule):
        resp = await client.delete(f"/api/v1/schedules/{sample_schedule.id}", cookies=auth_cookies)
        assert resp.status_code == 204

    async def test_delete_not_found(self, client: AsyncClient, auth_cookies):
        resp = await client.delete(f"/api/v1/schedules/{uuid.uuid4()}", cookies=auth_cookies)
        assert resp.status_code == 404
