"""Pydantic schemas for comment endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class CommentReplyResponse(BaseModel):
    id: uuid.UUID
    comment_id: uuid.UUID
    reply_text: str
    ai_suggested_text: str | None
    reply_mode: str
    status: str
    sent_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CommentResponse(BaseModel):
    id: uuid.UUID
    published_post_id: uuid.UUID
    platform: str
    platform_comment_id: str
    commenter_name: str | None
    commenter_username: str | None
    commenter_profile_url: str | None
    commenter_follower_count: int | None
    comment_text: str
    is_mention: bool
    sentiment: str | None
    comment_type: str | None
    commented_at: datetime | None
    created_at: datetime
    replies: list[CommentReplyResponse] = []

    model_config = {"from_attributes": True}


class CommentListResponse(BaseModel):
    items: list[CommentResponse]
    total: int
    page: int
    page_size: int
    pages: int


class GenerateReplyRequest(BaseModel):
    tone: str = "professional"


class SendReplyRequest(BaseModel):
    reply_text: str


class DismissCommentRequest(BaseModel):
    reason: str | None = None
