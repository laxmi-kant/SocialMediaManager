"""Pydantic schemas for schedule endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CreateScheduleRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    platform: str = Field(pattern="^(twitter|linkedin)$")
    content_types: list[str] = Field(min_length=1)
    cron_expression: str = Field(min_length=1, max_length=100)
    timezone: str = Field(default="UTC", max_length=100)
    auto_approve: bool = False


class UpdateScheduleRequest(BaseModel):
    name: str | None = None
    content_types: list[str] | None = None
    cron_expression: str | None = None
    timezone: str | None = None
    auto_approve: bool | None = None
    is_active: bool | None = None


class ScheduleResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    platform: str
    content_types: list[str]
    cron_expression: str
    timezone: str
    auto_approve: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ScheduleListResponse(BaseModel):
    items: list[ScheduleResponse]
    total: int
