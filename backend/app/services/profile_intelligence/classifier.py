"""AI-powered lead status classification (OPEN_TO_WORK, HIRING, etc.)."""

import structlog

from app.models.lead import LinkedInLead
from app.services.ai_generator.client import AnthropicClientWrapper

logger = structlog.get_logger()

CLASSIFY_PROMPT = """Analyze this LinkedIn profile and classify the person's status.
Return ONLY one of these labels: OPEN_TO_WORK, HIRING, BUSINESS, GENERAL

Profile:
- Name: {name}
- Headline: {headline}
- Company: {company}
- Industry: {industry}
- Location: {location}

Rules:
- OPEN_TO_WORK: headline/profile mentions looking for work, open to opportunities, seeking roles
- HIRING: headline mentions hiring, recruiting, looking for talent, "we're hiring"
- BUSINESS: headline mentions CEO, founder, agency, consulting, freelance, services
- GENERAL: default if unclear

Response (single word):"""

VALID_STATUSES = {"OPEN_TO_WORK", "HIRING", "BUSINESS", "GENERAL"}


class LeadStatusClassifier:
    """Classifies leads using Claude AI based on profile data."""

    def __init__(self, ai_client: AnthropicClientWrapper | None = None):
        self.ai_client = ai_client or AnthropicClientWrapper()

    def classify(self, lead: LinkedInLead) -> str:
        """Classify a lead and return status string."""
        try:
            result = self.ai_client.generate(
                prompt=CLASSIFY_PROMPT.format(
                    name=lead.name or "Unknown",
                    headline=lead.headline or "N/A",
                    company=lead.current_company or "N/A",
                    industry=lead.industry or "N/A",
                    location=lead.location or "N/A",
                ),
                max_tokens=10,
            )
            status = result.text.strip().upper()
            if status in VALID_STATUSES:
                return status

            logger.warning("invalid_lead_status", raw=result.text)
            return "GENERAL"
        except Exception as exc:
            logger.warning("lead_classify_error", error=str(exc))
            return "GENERAL"
