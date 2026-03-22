"""Integration tests for comments API endpoints."""

import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment
from app.models.generated_post import GeneratedPost
from app.models.platform_account import PlatformAccount
from app.models.published_post import PublishedPost
from app.models.user import User
from app.utils.security import create_access_token


@pytest.fixture
def auth_cookies(test_user: User) -> dict:
    token = create_access_token(test_user.id)
    return {"access_token": token}


@pytest_asyncio.fixture
async def setup_comments(db_session: AsyncSession, test_user: User):
    """Create a full chain: user -> generated_post -> platform_account -> published_post -> comments."""
    gen_post = GeneratedPost(
        user_id=test_user.id,
        target_platform="linkedin",
        content_text="Test post",
        content_type="tech_insight",
        tone="professional",
        status="published",
    )
    db_session.add(gen_post)
    await db_session.flush()

    account = PlatformAccount(
        user_id=test_user.id,
        platform="linkedin",
        platform_user_id="li-123",
        display_name="Test User",
        access_token="encrypted_token",
        is_active=True,
    )
    db_session.add(account)
    await db_session.flush()

    pub_post = PublishedPost(
        generated_post_id=gen_post.id,
        platform_account_id=account.id,
        platform_post_id="urn:li:share:999",
        status="success",
    )
    db_session.add(pub_post)
    await db_session.flush()

    comments = []
    for i in range(3):
        c = Comment(
            published_post_id=pub_post.id,
            platform="linkedin",
            platform_comment_id=f"comment-{i}",
            commenter_name=f"User {i}",
            comment_text=f"Test comment {i}",
            sentiment=["positive", "negative", "question"][i],
            comment_type=["praise", "complaint", "question"][i],
        )
        db_session.add(c)
        comments.append(c)

    await db_session.commit()
    for c in comments:
        await db_session.refresh(c)

    return {"comments": comments, "gen_post": gen_post, "pub_post": pub_post, "account": account}


@pytest.mark.asyncio
class TestListComments:
    async def test_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/v1/comments")
        assert resp.status_code == 401

    async def test_list_comments(self, client: AsyncClient, auth_cookies, setup_comments):
        resp = await client.get("/api/v1/comments", cookies=auth_cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3

    async def test_filter_by_sentiment(self, client: AsyncClient, auth_cookies, setup_comments):
        resp = await client.get("/api/v1/comments", params={"sentiment": "positive"}, cookies=auth_cookies)
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    async def test_filter_by_type(self, client: AsyncClient, auth_cookies, setup_comments):
        resp = await client.get("/api/v1/comments", params={"comment_type": "question"}, cookies=auth_cookies)
        assert resp.status_code == 200
        assert resp.json()["total"] == 1


@pytest.mark.asyncio
class TestCommentStats:
    async def test_stats(self, client: AsyncClient, auth_cookies, setup_comments):
        resp = await client.get("/api/v1/comments/stats", cookies=auth_cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_comments"] == 3
        assert data["unreplied_comments"] == 3
        assert data["replied_comments"] == 0

    async def test_stats_empty(self, client: AsyncClient, auth_cookies):
        resp = await client.get("/api/v1/comments/stats", cookies=auth_cookies)
        assert resp.status_code == 200
        assert resp.json()["total_comments"] == 0
