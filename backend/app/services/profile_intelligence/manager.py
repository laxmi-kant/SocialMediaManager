"""Orchestrates profile collection, enrichment, and classification."""

from datetime import datetime, timedelta, timezone

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.lead import LinkedInLead
from app.models.platform_account import PlatformAccount
from app.models.published_post import PublishedPost
from app.services.profile_intelligence.classifier import LeadStatusClassifier
from app.services.profile_intelligence.collector import LinkedInProfileCollector

logger = structlog.get_logger()


class LeadManager:
    """High-level orchestrator for lead intelligence pipeline."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.collector = LinkedInProfileCollector(db)
        self.classifier = LeadStatusClassifier()

    async def collect_all_engagers(self, user_id) -> int:
        """Collect engagers from all recent published posts for a user."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)

        result = await self.db.execute(
            select(PublishedPost)
            .where(
                PublishedPost.status == "success",
                PublishedPost.published_at >= cutoff,
            )
            .options(joinedload(PublishedPost.platform_account))
        )
        posts = result.unique().scalars().all()

        total_leads = 0
        for pub_post in posts:
            account = pub_post.platform_account
            if not account or account.platform != "linkedin":
                continue
            if not account.is_active or account.user_id != user_id:
                continue

            leads = await self.collector.collect_engagers_for_post(pub_post, account)
            total_leads += len(leads)

        await self.db.commit()
        logger.info("collect_all_complete", user_id=str(user_id), total=total_leads)
        return total_leads

    async def enrich_and_classify_leads(self, user_id, limit: int = 20) -> int:
        """Enrich unclassified leads with profile data and classify them."""
        # Get user's LinkedIn account for API access
        acct_result = await self.db.execute(
            select(PlatformAccount).where(
                PlatformAccount.user_id == user_id,
                PlatformAccount.platform == "linkedin",
                PlatformAccount.is_active.is_(True),
            )
        )
        account = acct_result.scalar_one_or_none()
        if not account:
            logger.warning("no_linkedin_account", user_id=str(user_id))
            return 0

        # Find leads without classification
        result = await self.db.execute(
            select(LinkedInLead)
            .where(
                LinkedInLead.user_id == user_id,
                LinkedInLead.ai_status.is_(None),
            )
            .limit(limit)
        )
        leads = result.scalars().all()

        processed = 0
        for lead in leads:
            # Enrich if missing name
            if not lead.name or not lead.headline:
                await self.collector.enrich_lead_profile(lead, account)

            # Classify
            lead.ai_status = self.classifier.classify(lead)
            processed += 1

        await self.db.commit()
        logger.info("enrich_classify_complete", processed=processed)
        return processed
