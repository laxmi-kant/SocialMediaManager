"""Posts API routes - CRUD, approve, reject, schedule."""

import math
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.generated_post import GeneratedPost
from app.models.platform_account import PlatformAccount
from app.models.published_post import PublishedPost
from app.models.user import User
from app.schemas.post import (
    PostListResponse,
    PostResponse,
    SchedulePostRequest,
    UpdatePostRequest,
)
from app.services.publishers.registry import publisher_registry

router = APIRouter(prefix="/posts", tags=["posts"])


async def _get_user_post(post_id: str, user: User, db: AsyncSession) -> GeneratedPost:
    try:
        uid = uuid.UUID(post_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid post ID")

    result = await db.execute(
        select(GeneratedPost).where(GeneratedPost.id == uid, GeneratedPost.user_id == user.id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.get("", response_model=PostListResponse)
async def list_posts(
    status_filter: str | None = Query(default=None, alias="status"),
    target_platform: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = select(GeneratedPost).where(GeneratedPost.user_id == user.id)
    count_query = select(func.count()).select_from(GeneratedPost).where(GeneratedPost.user_id == user.id)

    if status_filter:
        query = query.where(GeneratedPost.status == status_filter)
        count_query = count_query.where(GeneratedPost.status == status_filter)
    if target_platform:
        query = query.where(GeneratedPost.target_platform == target_platform)
        count_query = count_query.where(GeneratedPost.target_platform == target_platform)

    query = query.order_by(GeneratedPost.created_at.desc())
    total = (await db.execute(count_query)).scalar_one()
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PostListResponse(
        items=[PostResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 0,
    )


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await _get_user_post(post_id, user, db)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str,
    data: UpdatePostRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    post = await _get_user_post(post_id, user, db)
    if post.status == "published":
        raise HTTPException(status_code=400, detail="Cannot edit a published post")

    if data.content_text is not None:
        post.content_text = data.content_text
    if data.hashtags is not None:
        post.hashtags = data.hashtags
    if data.tone is not None:
        post.tone = data.tone

    await db.flush()
    await db.refresh(post)
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    post = await _get_user_post(post_id, user, db)
    if post.status == "published":
        raise HTTPException(status_code=400, detail="Cannot delete a published post")
    await db.delete(post)


@router.post("/{post_id}/approve", response_model=PostResponse)
async def approve_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    post = await _get_user_post(post_id, user, db)
    if post.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft posts can be approved")
    post.status = "approved"
    await db.flush()
    await db.refresh(post)
    return post


@router.post("/{post_id}/reject", response_model=PostResponse)
async def reject_post(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    post = await _get_user_post(post_id, user, db)
    if post.status not in ("draft", "approved"):
        raise HTTPException(status_code=400, detail="Post cannot be rejected in current status")
    post.status = "rejected"
    await db.flush()
    await db.refresh(post)
    return post


@router.post("/{post_id}/schedule", response_model=PostResponse)
async def schedule_post(
    post_id: str,
    data: SchedulePostRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    post = await _get_user_post(post_id, user, db)
    if post.status != "approved":
        raise HTTPException(status_code=400, detail="Only approved posts can be scheduled")
    if data.scheduled_for < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Scheduled time must be in the future")

    post.status = "scheduled"
    post.scheduled_for = data.scheduled_for
    await db.flush()
    await db.refresh(post)
    return post


@router.post("/{post_id}/publish", response_model=PostResponse)
async def publish_post_now(
    post_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    post = await _get_user_post(post_id, user, db)
    if post.status not in ("approved", "scheduled"):
        raise HTTPException(status_code=400, detail="Only approved or scheduled posts can be published")

    # Find user's platform account for this target platform
    result = await db.execute(
        select(PlatformAccount).where(
            PlatformAccount.user_id == user.id,
            PlatformAccount.platform == post.target_platform,
            PlatformAccount.is_active == True,
        )
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(
            status_code=400,
            detail=f"No active {post.target_platform} account connected. Please connect in Settings.",
        )

    # Publish via the appropriate publisher
    publisher = publisher_registry.get(post.target_platform)
    pub_result = await publisher.publish(
        text=post.content_text,
        hashtags=post.hashtags or [],
        account=account,
    )

    if pub_result.success:
        post.status = "published"
        published = PublishedPost(
            generated_post_id=post.id,
            platform_account_id=account.id,
            platform_post_id=pub_result.platform_post_id,
            platform_url=pub_result.platform_url,
            status="success",
        )
        db.add(published)
    else:
        post.status = "failed"
        published = PublishedPost(
            generated_post_id=post.id,
            platform_account_id=account.id,
            status="failed",
            error_message=pub_result.error_message,
        )
        db.add(published)
        await db.flush()
        await db.refresh(post)
        raise HTTPException(status_code=502, detail=f"Publishing failed: {pub_result.error_message}")

    await db.flush()
    await db.refresh(post)
    return post
