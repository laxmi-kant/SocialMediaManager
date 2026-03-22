"""Integration tests for posts API endpoints."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_source import ContentSource
from app.models.generated_post import GeneratedPost
from app.models.user import User
from app.utils.security import create_access_token


@pytest.fixture
def auth_cookies(test_user: User) -> dict:
    token = create_access_token(test_user.id)
    return {"access_token": token}


@pytest_asyncio.fixture
async def sample_post(db_session: AsyncSession, test_user: User) -> GeneratedPost:
    post = GeneratedPost(
        user_id=test_user.id,
        target_platform="twitter",
        content_text="Test tweet about AI #AI #Tech",
        content_type="tech_insight",
        tone="professional",
        hashtags=["#AI", "#Tech"],
        ai_model="claude-haiku-4-5-20251001",
        status="draft",
    )
    db_session.add(post)
    await db_session.commit()
    await db_session.refresh(post)
    return post


@pytest_asyncio.fixture
async def approved_post(db_session: AsyncSession, test_user: User) -> GeneratedPost:
    post = GeneratedPost(
        user_id=test_user.id,
        target_platform="linkedin",
        content_text="Great insights on AI today. #AI",
        content_type="news_commentary",
        tone="professional",
        hashtags=["#AI"],
        status="approved",
    )
    db_session.add(post)
    await db_session.commit()
    await db_session.refresh(post)
    return post


@pytest.mark.asyncio
class TestListPosts:
    async def test_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/v1/posts")
        assert resp.status_code == 401

    async def test_returns_user_posts(self, client: AsyncClient, auth_cookies, sample_post):
        resp = await client.get("/api/v1/posts", cookies=auth_cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["id"] == str(sample_post.id)

    async def test_filter_by_status(self, client: AsyncClient, auth_cookies, sample_post, approved_post):
        resp = await client.get("/api/v1/posts", params={"status": "draft"}, cookies=auth_cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "draft"

    async def test_filter_by_platform(self, client: AsyncClient, auth_cookies, sample_post, approved_post):
        resp = await client.get("/api/v1/posts", params={"target_platform": "linkedin"}, cookies=auth_cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["target_platform"] == "linkedin"

    async def test_pagination(self, client: AsyncClient, auth_cookies, sample_post, approved_post):
        resp = await client.get("/api/v1/posts", params={"page_size": 1}, cookies=auth_cookies)
        data = resp.json()
        assert data["total"] == 2
        assert len(data["items"]) == 1
        assert data["pages"] == 2


@pytest.mark.asyncio
class TestGetPost:
    async def test_get_by_id(self, client: AsyncClient, auth_cookies, sample_post):
        resp = await client.get(f"/api/v1/posts/{sample_post.id}", cookies=auth_cookies)
        assert resp.status_code == 200
        assert resp.json()["content_text"] == "Test tweet about AI #AI #Tech"

    async def test_not_found(self, client: AsyncClient, auth_cookies):
        resp = await client.get(f"/api/v1/posts/{uuid.uuid4()}", cookies=auth_cookies)
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestUpdatePost:
    async def test_update_content(self, client: AsyncClient, auth_cookies, sample_post):
        resp = await client.put(
            f"/api/v1/posts/{sample_post.id}",
            json={"content_text": "Updated tweet #NewTag"},
            cookies=auth_cookies,
        )
        assert resp.status_code == 200
        assert resp.json()["content_text"] == "Updated tweet #NewTag"

    async def test_update_hashtags(self, client: AsyncClient, auth_cookies, sample_post):
        resp = await client.put(
            f"/api/v1/posts/{sample_post.id}",
            json={"hashtags": ["#New", "#Tags"]},
            cookies=auth_cookies,
        )
        assert resp.status_code == 200
        assert resp.json()["hashtags"] == ["#New", "#Tags"]

    async def test_cannot_edit_published(self, client: AsyncClient, auth_cookies, db_session, sample_post):
        sample_post.status = "published"
        await db_session.commit()

        resp = await client.put(
            f"/api/v1/posts/{sample_post.id}",
            json={"content_text": "Try to edit"},
            cookies=auth_cookies,
        )
        assert resp.status_code == 400
        assert "published" in resp.json()["detail"].lower()


@pytest.mark.asyncio
class TestDeletePost:
    async def test_delete_draft(self, client: AsyncClient, auth_cookies, sample_post):
        resp = await client.delete(f"/api/v1/posts/{sample_post.id}", cookies=auth_cookies)
        assert resp.status_code == 204

        # Verify deleted
        resp = await client.get(f"/api/v1/posts/{sample_post.id}", cookies=auth_cookies)
        assert resp.status_code == 404

    async def test_cannot_delete_published(self, client: AsyncClient, auth_cookies, db_session, sample_post):
        sample_post.status = "published"
        await db_session.commit()

        resp = await client.delete(f"/api/v1/posts/{sample_post.id}", cookies=auth_cookies)
        assert resp.status_code == 400


@pytest.mark.asyncio
class TestApprovePost:
    async def test_approve_draft(self, client: AsyncClient, auth_cookies, sample_post):
        resp = await client.post(f"/api/v1/posts/{sample_post.id}/approve", cookies=auth_cookies)
        assert resp.status_code == 200
        assert resp.json()["status"] == "approved"

    async def test_cannot_approve_non_draft(self, client: AsyncClient, auth_cookies, approved_post):
        resp = await client.post(f"/api/v1/posts/{approved_post.id}/approve", cookies=auth_cookies)
        assert resp.status_code == 400


@pytest.mark.asyncio
class TestRejectPost:
    async def test_reject_draft(self, client: AsyncClient, auth_cookies, sample_post):
        resp = await client.post(f"/api/v1/posts/{sample_post.id}/reject", cookies=auth_cookies)
        assert resp.status_code == 200
        assert resp.json()["status"] == "rejected"

    async def test_reject_approved(self, client: AsyncClient, auth_cookies, approved_post):
        resp = await client.post(f"/api/v1/posts/{approved_post.id}/reject", cookies=auth_cookies)
        assert resp.status_code == 200
        assert resp.json()["status"] == "rejected"

    async def test_cannot_reject_published(self, client: AsyncClient, auth_cookies, db_session, sample_post):
        sample_post.status = "published"
        await db_session.commit()

        resp = await client.post(f"/api/v1/posts/{sample_post.id}/reject", cookies=auth_cookies)
        assert resp.status_code == 400


@pytest.mark.asyncio
class TestSchedulePost:
    async def test_schedule_approved(self, client: AsyncClient, auth_cookies, approved_post):
        future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        resp = await client.post(
            f"/api/v1/posts/{approved_post.id}/schedule",
            json={"scheduled_for": future},
            cookies=auth_cookies,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "scheduled"
        assert resp.json()["scheduled_for"] is not None

    async def test_cannot_schedule_draft(self, client: AsyncClient, auth_cookies, sample_post):
        future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        resp = await client.post(
            f"/api/v1/posts/{sample_post.id}/schedule",
            json={"scheduled_for": future},
            cookies=auth_cookies,
        )
        assert resp.status_code == 400

    async def test_cannot_schedule_in_past(self, client: AsyncClient, auth_cookies, approved_post):
        past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        resp = await client.post(
            f"/api/v1/posts/{approved_post.id}/schedule",
            json={"scheduled_for": past},
            cookies=auth_cookies,
        )
        assert resp.status_code == 400
