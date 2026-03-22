"""Pydantic schemas for lead endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class LeadEngagementResponse(BaseModel):
    id: uuid.UUID
    engagement_type: str
    engagement_text: str | None
    engaged_at: datetime

    model_config = {"from_attributes": True}


class LeadResponse(BaseModel):
    id: uuid.UUID
    linkedin_member_id: str
    name: str | None
    headline: str | None
    current_company: str | None
    profile_url: str | None
    email: str | None
    location: str | None
    industry: str | None
    ai_status: str | None
    tags: list[str] | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    engagements: list[LeadEngagementResponse] = []

    model_config = {"from_attributes": True}


class LeadListResponse(BaseModel):
    items: list[LeadResponse]
    total: int
    page: int
    page_size: int
    pages: int


class UpdateLeadRequest(BaseModel):
    tags: list[str] | None = None
    notes: str | None = None


class LeadStatsResponse(BaseModel):
    total_leads: int
    open_to_work: int
    hiring: int
    has_email: int
