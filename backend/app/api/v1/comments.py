"""Comments API routes - list, reply, generate-reply, dismiss."""

import math
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.api.deps import get_current_user
from app.database import get_db
from app.models.comment import Comment, CommentReply
from app.models.generated_post import GeneratedPost
from app.models.platform_account import PlatformAccount
from app.models.published_post import PublishedPost
from app.models.user import User
from app.schemas.comment import (
    CommentListResponse,
    CommentResponse,
    CommentReplyResponse,
    GenerateReplyRequest,
    SendReplyRequest,
)
from app.services.comments.auto_reply import AutoReplyProcessor
from app.services.comments.reply_generator import CommentReplyGenerator
from app.utils.http_client import ResilientHTTPClient
from app.utils.security import decrypt_token

router = APIRouter(prefix="/comments", tags=["comments"])


async def _get_user_comments_query(user: User, db: AsyncSession):
    """Base query for comments belonging to the user's published posts."""
    return (
        select(Comment)
        .join(PublishedPost, Comment.published_post_id == PublishedPost.id)
        .join(GeneratedPost, PublishedPost.generated_post_id == GeneratedPost.id)
        .where(GeneratedPost.user_id == user.id)
    )


@router.get("", response_model=CommentListResponse)
async def list_comments(
    sentiment: str | None = Query(default=None),
    comment_type: str | None = Query(default=None),
    has_reply: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    base = await _get_user_comments_query(user, db)
    count_base = (
        select(func.count())
        .select_from(Comment)
        .join(PublishedPost, Comment.published_post_id == PublishedPost.id)
        .join(GeneratedPost, PublishedPost.generated_post_id == GeneratedPost.id)
        .where(GeneratedPost.user_id == user.id)
    )

    if sentiment:
        base = base.where(Comment.sentiment == sentiment)
        count_base = count_base.where(Comment.sentiment == sentiment)
    if comment_type:
        base = base.where(Comment.comment_type == comment_type)
        count_base = count_base.where(Comment.comment_type == comment_type)

    total = (await db.execute(count_base)).scalar_one()

    query = (
        base.options(joinedload(Comment.replies))
        .order_by(Comment.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    items = result.unique().scalars().all()

    return CommentListResponse(
        items=[CommentResponse.model_validate(c) for c in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 0,
    )


@router.post("/{comment_id}/generate-reply", response_model=CommentReplyResponse)
async def generate_reply(
    comment_id: str,
    data: GenerateReplyRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        cid = uuid.UUID(comment_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid comment ID")

    # Verify comment belongs to user
    base = await _get_user_comments_query(user, db)
    result = await db.execute(base.where(Comment.id == cid))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Get post text for context
    pub = await db.get(PublishedPost, comment.published_post_id)
    gen_post = await db.get(GeneratedPost, pub.generated_post_id) if pub else None
    post_text = gen_post.content_text if gen_post else ""

    generator = CommentReplyGenerator()
    reply = generator.generate_reply(comment, post_text, tone=data.tone)
    db.add(reply)
    await db.flush()
    await db.refresh(reply)
    return reply


@router.post("/{comment_id}/reply", response_model=CommentReplyResponse)
async def send_reply(
    comment_id: str,
    data: SendReplyRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        cid = uuid.UUID(comment_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid comment ID")

    base = await _get_user_comments_query(user, db)
    result = await db.execute(base.where(Comment.id == cid))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Get platform account to send reply
    pub = await db.get(PublishedPost, comment.published_post_id)
    if not pub:
        raise HTTPException(status_code=400, detail="Published post not found")

    account_result = await db.execute(
        select(PlatformAccount).where(PlatformAccount.id == pub.platform_account_id)
    )
    account = account_result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=400, detail="Platform account not found")

    # Send to LinkedIn
    reply = CommentReply(
        comment_id=cid,
        reply_text=data.reply_text,
        reply_mode="manual",
        status="sending",
    )
    db.add(reply)
    await db.flush()

    try:
        token = decrypt_token(account.access_token)
        headers = {
            "Authorization": f"Bearer {token}",
            "LinkedIn-Version": "202402",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        async with ResilientHTTPClient("linkedin") as client:
            resp = await client.post(
                f"https://api.linkedin.com/rest/socialActions/{pub.platform_post_id}/comments",
                json={
                    "actor": f"urn:li:person:{account.platform_user_id}",
                    "message": {"text": data.reply_text},
                },
                headers=headers,
            )
            reply.platform_reply_id = resp.headers.get("x-restli-id", "")
            reply.status = "sent"
            from datetime import datetime, timezone
            reply.sent_at = datetime.now(timezone.utc)
    except Exception as exc:
        reply.status = "failed"
        reply.error_message = str(exc)
        raise HTTPException(status_code=502, detail=f"Failed to send reply: {exc}")
    finally:
        await db.flush()
        await db.refresh(reply)

    return reply


@router.get("/stats")
async def comment_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get comment statistics for the dashboard."""
    base_where = (
        select(func.count())
        .select_from(Comment)
        .join(PublishedPost, Comment.published_post_id == PublishedPost.id)
        .join(GeneratedPost, PublishedPost.generated_post_id == GeneratedPost.id)
        .where(GeneratedPost.user_id == user.id)
    )

    total = (await db.execute(base_where)).scalar_one()

    # Comments without any replies
    unreplied_q = (
        select(func.count())
        .select_from(Comment)
        .join(PublishedPost, Comment.published_post_id == PublishedPost.id)
        .join(GeneratedPost, PublishedPost.generated_post_id == GeneratedPost.id)
        .where(
            GeneratedPost.user_id == user.id,
            ~Comment.replies.any(),
        )
    )
    unreplied = (await db.execute(unreplied_q)).scalar_one()

    return {
        "total_comments": total,
        "unreplied_comments": unreplied,
        "replied_comments": total - unreplied,
    }
