"""Integration tests for platform API endpoints."""

import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.platform_account import PlatformAccount
from app.models.user import User
from app.utils.security import create_access_token, encrypt_token


@pytest.fixture
def auth_cookies(test_user: User) -> dict:
    token = create_access_token(test_user.id)
    return {"access_token": token}


@pytest_asyncio.fixture
async def twitter_account(db_session: AsyncSession, test_user: User) -> PlatformAccount:
    # Need a valid Fernet key for encryption in tests
    account = PlatformAccount(
        user_id=test_user.id,
        platform="twitter",
        platform_user_id="123456",
        display_name="@testuser",
        access_token="encrypted_fake_token",
        scopes=["tweet.read", "tweet.write"],
        is_active=True,
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest.mark.asyncio
class TestListPlatforms:
    async def test_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/v1/platforms")
        assert resp.status_code == 401

    async def test_list_empty(self, client: AsyncClient, auth_cookies):
        resp = await client.get("/api/v1/platforms", cookies=auth_cookies)
        assert resp.status_code == 200
        assert resp.json()["platforms"] == []

    async def test_list_with_account(self, client: AsyncClient, auth_cookies, twitter_account):
        resp = await client.get("/api/v1/platforms", cookies=auth_cookies)
        assert resp.status_code == 200
        platforms = resp.json()["platforms"]
        assert len(platforms) == 1
        assert platforms[0]["platform"] == "twitter"
        assert platforms[0]["display_name"] == "@testuser"


@pytest.mark.asyncio
class TestDisconnectPlatform:
    async def test_disconnect(self, client: AsyncClient, auth_cookies, twitter_account):
        resp = await client.delete(f"/api/v1/platforms/{twitter_account.id}", cookies=auth_cookies)
        assert resp.status_code == 204

        # Verify it's gone
        resp = await client.get("/api/v1/platforms", cookies=auth_cookies)
        assert resp.json()["platforms"] == []

    async def test_disconnect_not_found(self, client: AsyncClient, auth_cookies):
        resp = await client.delete(f"/api/v1/platforms/{uuid.uuid4()}", cookies=auth_cookies)
        assert resp.status_code == 404

    async def test_disconnect_invalid_id(self, client: AsyncClient, auth_cookies):
        resp = await client.delete("/api/v1/platforms/not-a-uuid", cookies=auth_cookies)
        assert resp.status_code == 400


@pytest.mark.asyncio
class TestOAuthAuthorize:
    async def test_twitter_authorize_not_configured(self, client: AsyncClient, auth_cookies):
        # With default empty config, should return 400
        resp = await client.get(
            "/api/v1/platforms/twitter/authorize",
            cookies=auth_cookies,
            follow_redirects=False,
        )
        assert resp.status_code == 400

    async def test_linkedin_authorize_not_configured(self, client: AsyncClient, auth_cookies):
        resp = await client.get(
            "/api/v1/platforms/linkedin/authorize",
            cookies=auth_cookies,
            follow_redirects=False,
        )
        assert resp.status_code == 400
