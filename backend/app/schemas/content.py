"""Pydantic schemas for content source endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class ContentSourceResponse(BaseModel):
    id: uuid.UUID
    source_type: str
    external_id: str | None
    title: str
    url: str | None
    content: str | None
    author: str | None
    score: int
    tags: list[str] | None
    metadata: dict | None
    fetched_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class ContentListResponse(BaseModel):
    items: list[ContentSourceResponse]
    total: int
    page: int
    page_size: int
    pages: int
