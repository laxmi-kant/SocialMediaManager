"""Integration tests for leads API endpoints."""

import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import LinkedInLead
from app.models.user import User
from app.utils.security import create_access_token


@pytest.fixture
def auth_cookies(test_user: User) -> dict:
    token = create_access_token(test_user.id)
    return {"access_token": token}


@pytest_asyncio.fixture
async def setup_leads(db_session: AsyncSession, test_user: User):
    """Create test leads."""
    leads = []
    statuses = ["OPEN_TO_WORK", "HIRING", "BUSINESS", "GENERAL"]
    for i in range(4):
        lead = LinkedInLead(
            user_id=test_user.id,
            linkedin_member_id=f"member-{i}",
            name=f"Lead {i}",
            headline=f"Headline {i}",
            current_company=f"Company {i}",
            location="San Francisco" if i < 2 else "New York",
            ai_status=statuses[i],
            email=f"lead{i}@example.com" if i < 2 else None,
            tags=["tech", "ai"] if i == 0 else None,
        )
        db_session.add(lead)
        leads.append(lead)

    await db_session.commit()
    for lead in leads:
        await db_session.refresh(lead)

    return leads


@pytest.mark.asyncio
class TestListLeads:
    async def test_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/v1/leads")
        assert resp.status_code == 401

    async def test_list_leads(self, client: AsyncClient, auth_cookies, setup_leads):
        resp = await client.get("/api/v1/leads", cookies=auth_cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 4
        assert len(data["items"]) == 4

    async def test_filter_by_status(self, client: AsyncClient, auth_cookies, setup_leads):
        resp = await client.get(
            "/api/v1/leads", params={"ai_status": "HIRING"}, cookies=auth_cookies
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["ai_status"] == "HIRING"

    async def test_search_by_name(self, client: AsyncClient, auth_cookies, setup_leads):
        resp = await client.get(
            "/api/v1/leads", params={"search": "Lead 0"}, cookies=auth_cookies
        )
        assert resp.status_code == 200
        assert resp.json()["total"] == 1


@pytest.mark.asyncio
class TestLeadStats:
    async def test_stats(self, client: AsyncClient, auth_cookies, setup_leads):
        resp = await client.get("/api/v1/leads/stats", cookies=auth_cookies)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_leads"] == 4
        assert data["open_to_work"] == 1
        assert data["hiring"] == 1
        assert data["has_email"] == 2

    async def test_stats_empty(self, client: AsyncClient, auth_cookies):
        resp = await client.get("/api/v1/leads/stats", cookies=auth_cookies)
        assert resp.status_code == 200
        assert resp.json()["total_leads"] == 0


@pytest.mark.asyncio
class TestLeadDetail:
    async def test_get_lead(self, client: AsyncClient, auth_cookies, setup_leads):
        lead_id = str(setup_leads[0].id)
        resp = await client.get(f"/api/v1/leads/{lead_id}", cookies=auth_cookies)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Lead 0"

    async def test_get_not_found(self, client: AsyncClient, auth_cookies):
        fake_id = str(uuid.uuid4())
        resp = await client.get(f"/api/v1/leads/{fake_id}", cookies=auth_cookies)
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestUpdateLead:
    async def test_update_tags_and_notes(self, client: AsyncClient, auth_cookies, setup_leads):
        lead_id = str(setup_leads[0].id)
        resp = await client.patch(
            f"/api/v1/leads/{lead_id}",
            json={"tags": ["sales", "warm"], "notes": "Interested in our product"},
            cookies=auth_cookies,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["tags"] == ["sales", "warm"]
        assert data["notes"] == "Interested in our product"


@pytest.mark.asyncio
class TestDeleteLead:
    async def test_delete_lead(self, client: AsyncClient, auth_cookies, setup_leads):
        lead_id = str(setup_leads[0].id)
        resp = await client.delete(f"/api/v1/leads/{lead_id}", cookies=auth_cookies)
        assert resp.status_code == 204

        # Verify deleted
        resp = await client.get(f"/api/v1/leads/{lead_id}", cookies=auth_cookies)
        assert resp.status_code == 404

    async def test_delete_not_found(self, client: AsyncClient, auth_cookies):
        fake_id = str(uuid.uuid4())
        resp = await client.delete(f"/api/v1/leads/{fake_id}", cookies=auth_cookies)
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestExportLeads:
    async def test_export_csv(self, client: AsyncClient, auth_cookies, setup_leads):
        resp = await client.get("/api/v1/leads/export", cookies=auth_cookies)
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
        lines = resp.text.strip().split("\n")
        assert len(lines) == 5  # header + 4 leads
        assert "Name" in lines[0]

    async def test_export_filtered(self, client: AsyncClient, auth_cookies, setup_leads):
        resp = await client.get(
            "/api/v1/leads/export", params={"ai_status": "HIRING"}, cookies=auth_cookies
        )
        assert resp.status_code == 200
        lines = resp.text.strip().split("\n")
        assert len(lines) == 2  # header + 1 lead
