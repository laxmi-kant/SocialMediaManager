"""Tests for LinkedInProfileCollector."""

import uuid

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import LeadEngagement, LinkedInLead
from app.models.user import User
from app.utils.security import hash_password


@pytest_asyncio.fixture
async def user_for_collector(db_session: AsyncSession) -> User:
    user = User(
        id=uuid.uuid4(),
        email="collector@example.com",
        password_hash=hash_password("TestPass123"),
        full_name="Collector User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
class TestCollectorUpsertLead:
    async def test_creates_new_lead(self, db_session: AsyncSession, user_for_collector: User):
        from app.services.profile_intelligence.collector import LinkedInProfileCollector

        collector = LinkedInProfileCollector(db_session)
        lead = await collector._upsert_lead(user_for_collector.id, "member123", "urn:li:person:member123")

        assert lead.id is not None
        assert lead.linkedin_member_id == "member123"
        assert lead.user_id == user_for_collector.id

    async def test_returns_existing_lead(self, db_session: AsyncSession, user_for_collector: User):
        from app.services.profile_intelligence.collector import LinkedInProfileCollector

        # Create first
        existing = LinkedInLead(
            user_id=user_for_collector.id,
            linkedin_member_id="member456",
            name="Existing Lead",
        )
        db_session.add(existing)
        await db_session.flush()

        collector = LinkedInProfileCollector(db_session)
        lead = await collector._upsert_lead(user_for_collector.id, "member456", "urn:li:person:member456")

        assert lead.id == existing.id
        assert lead.name == "Existing Lead"

    async def test_upsert_engagement_creates_new(self, db_session: AsyncSession, user_for_collector: User):
        from app.services.profile_intelligence.collector import LinkedInProfileCollector

        lead = LinkedInLead(
            user_id=user_for_collector.id,
            linkedin_member_id="member789",
        )
        db_session.add(lead)
        await db_session.flush()

        # Need a published post ID - use a random UUID (won't FK validate in SQLite tests)
        post_id = uuid.uuid4()

        collector = LinkedInProfileCollector(db_session)
        engagement = await collector._upsert_engagement(
            lead_id=lead.id,
            post_id=post_id,
            engagement_type="like",
        )

        assert engagement.lead_id == lead.id
        assert engagement.engagement_type == "like"
