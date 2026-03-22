"""Collect LinkedIn profile data from post engagements."""

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import LeadEngagement, LinkedInLead
from app.models.platform_account import PlatformAccount
from app.models.published_post import PublishedPost
from app.utils.http_client import ResilientHTTPClient
from app.utils.security import decrypt_token

logger = structlog.get_logger()

LINKEDIN_API = "https://api.linkedin.com/rest"


class LinkedInProfileCollector:
    """Collects profile info from people who engaged with posts."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def collect_engagers_for_post(
        self, pub_post: PublishedPost, account: PlatformAccount
    ) -> list[LinkedInLead]:
        """Fetch reactions/comments on a post and upsert lead records."""
        token = decrypt_token(account.access_token)
        headers = {
            "Authorization": f"Bearer {token}",
            "LinkedIn-Version": "202402",
            "X-Restli-Protocol-Version": "2.0.0",
        }

        leads: list[LinkedInLead] = []

        async with ResilientHTTPClient("linkedin") as client:
            # Fetch reactions
            reaction_leads = await self._collect_reactions(
                client, headers, pub_post, account.user_id
            )
            leads.extend(reaction_leads)

            # Fetch commenters
            comment_leads = await self._collect_commenters(
                client, headers, pub_post, account.user_id
            )
            leads.extend(comment_leads)

        await self.db.flush()
        logger.info(
            "engagers_collected",
            post_id=str(pub_post.id),
            lead_count=len(leads),
        )
        return leads

    async def _collect_reactions(
        self, client, headers, pub_post, user_id
    ) -> list[LinkedInLead]:
        """Collect profiles from post reactions (likes)."""
        leads = []
        try:
            resp = await client.get(
                f"{LINKEDIN_API}/socialActions/{pub_post.platform_post_id}/likes",
                headers=headers,
                params={"count": 100},
            )
            data = resp.json()

            for reaction in data.get("elements", []):
                actor_urn = reaction.get("actor", "")
                member_id = actor_urn.split(":")[-1] if actor_urn else None
                if not member_id:
                    continue

                lead = await self._upsert_lead(user_id, member_id, actor_urn)
                leads.append(lead)

                await self._upsert_engagement(
                    lead_id=lead.id,
                    post_id=pub_post.id,
                    engagement_type="like",
                )
        except Exception as exc:
            logger.warning("reaction_collect_error", error=str(exc))

        return leads

    async def _collect_commenters(
        self, client, headers, pub_post, user_id
    ) -> list[LinkedInLead]:
        """Collect profiles from post comments."""
        leads = []
        try:
            resp = await client.get(
                f"{LINKEDIN_API}/socialActions/{pub_post.platform_post_id}/comments",
                headers=headers,
                params={"count": 100},
            )
            data = resp.json()

            for comment in data.get("elements", []):
                actor_urn = comment.get("actor", "")
                member_id = actor_urn.split(":")[-1] if actor_urn else None
                if not member_id:
                    continue

                lead = await self._upsert_lead(user_id, member_id, actor_urn)
                leads.append(lead)

                comment_text = comment.get("message", {}).get("text", "")
                await self._upsert_engagement(
                    lead_id=lead.id,
                    post_id=pub_post.id,
                    engagement_type="comment",
                    engagement_text=comment_text[:500] if comment_text else None,
                )
        except Exception as exc:
            logger.warning("commenter_collect_error", error=str(exc))

        return leads

    async def _upsert_lead(
        self, user_id, member_id: str, actor_urn: str
    ) -> LinkedInLead:
        """Find or create a lead record."""
        result = await self.db.execute(
            select(LinkedInLead).where(
                LinkedInLead.user_id == user_id,
                LinkedInLead.linkedin_member_id == member_id,
            )
        )
        lead = result.scalar_one_or_none()

        if not lead:
            lead = LinkedInLead(
                user_id=user_id,
                linkedin_member_id=member_id,
                profile_url=f"https://www.linkedin.com/in/{member_id}",
            )
            self.db.add(lead)
            await self.db.flush()

        return lead

    async def enrich_lead_profile(
        self, lead: LinkedInLead, account: PlatformAccount
    ) -> LinkedInLead:
        """Enrich a lead record with full profile data from LinkedIn API."""
        token = decrypt_token(account.access_token)
        headers = {
            "Authorization": f"Bearer {token}",
            "LinkedIn-Version": "202402",
            "X-Restli-Protocol-Version": "2.0.0",
        }

        async with ResilientHTTPClient("linkedin") as client:
            try:
                resp = await client.get(
                    f"{LINKEDIN_API}/people/(id:{lead.linkedin_member_id})",
                    headers=headers,
                    params={
                        "projection": "(id,localizedFirstName,localizedLastName,"
                        "localizedHeadline,vanityName,profilePicture,"
                        "geoLocation,industryName)"
                    },
                )
                profile = resp.json()

                first = profile.get("localizedFirstName", "")
                last = profile.get("localizedLastName", "")
                lead.name = f"{first} {last}".strip() or lead.name
                lead.headline = profile.get("localizedHeadline") or lead.headline
                lead.industry = profile.get("industryName") or lead.industry

                vanity = profile.get("vanityName")
                if vanity:
                    lead.profile_url = f"https://www.linkedin.com/in/{vanity}"

                geo = profile.get("geoLocation", {})
                if geo:
                    lead.location = geo.get("name") or lead.location

                await self.db.flush()
                logger.info("lead_enriched", lead_id=str(lead.id), name=lead.name)
            except Exception as exc:
                logger.warning(
                    "lead_enrich_error",
                    lead_id=str(lead.id),
                    error=str(exc),
                )

        return lead

    async def _upsert_engagement(
        self,
        lead_id,
        post_id,
        engagement_type: str,
        engagement_text: str | None = None,
    ) -> LeadEngagement:
        """Find or create an engagement record."""
        result = await self.db.execute(
            select(LeadEngagement).where(
                LeadEngagement.lead_id == lead_id,
                LeadEngagement.published_post_id == post_id,
                LeadEngagement.engagement_type == engagement_type,
            )
        )
        engagement = result.scalar_one_or_none()

        if not engagement:
            engagement = LeadEngagement(
                lead_id=lead_id,
                published_post_id=post_id,
                engagement_type=engagement_type,
                engagement_text=engagement_text,
            )
            self.db.add(engagement)

        return engagement
