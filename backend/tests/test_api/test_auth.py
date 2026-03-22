"""Integration tests for authentication API endpoints."""

import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "new@example.com",
            "password": "StrongPass123",
            "full_name": "New User",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "new@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data

    async def test_register_duplicate_email(self, client: AsyncClient, test_user: User):
        resp = await client.post("/api/v1/auth/register", json={
            "email": test_user.email,
            "password": "StrongPass123",
        })
        assert resp.status_code == 409

    async def test_register_invalid_email(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "not-an-email",
            "password": "StrongPass123",
        })
        assert resp.status_code == 422

    async def test_register_short_password(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/register", json={
            "email": "short@example.com",
            "password": "short",
        })
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestLogin:
    async def test_login_success(self, client: AsyncClient, test_user: User):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "access_token" in resp.cookies

    async def test_login_wrong_password(self, client: AsyncClient, test_user: User):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "WrongPassword",
        })
        assert resp.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/login", json={
            "email": "nobody@example.com",
            "password": "TestPass123",
        })
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestMe:
    async def test_me_authenticated(self, client: AsyncClient, test_user: User):
        # Login first
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123",
        })
        token = login_resp.cookies.get("access_token")

        resp = await client.get("/api/v1/auth/me", cookies={"access_token": token})
        assert resp.status_code == 200
        assert resp.json()["email"] == "test@example.com"

    async def test_me_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestLogout:
    async def test_logout_clears_cookies(self, client: AsyncClient, test_user: User):
        # Login first
        await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123",
        })

        resp = await client.post("/api/v1/auth/logout")
        assert resp.status_code == 204
