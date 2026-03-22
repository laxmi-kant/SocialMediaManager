"""Pydantic schemas for platform account endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class PlatformAccountResponse(BaseModel):
    id: uuid.UUID
    platform: str
    platform_user_id: str | None
    display_name: str | None
    is_active: bool
    token_expires_at: datetime | None
    scopes: list[str] | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PlatformListResponse(BaseModel):
    platforms: list[PlatformAccountResponse]
