"""Content research API routes."""

import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.content_source import ContentSource
from app.models.user import User
from app.schemas.content import ContentListResponse, ContentSourceResponse
from app.schemas.post import GeneratePostRequest, PostResponse
from app.services.ai_generator.generator import PostGenerator

router = APIRouter(prefix="/content", tags=["content"])


@router.get("", response_model=ContentListResponse)
async def list_content(
    source_type: str | None = Query(default=None),
    sort_by: str = Query(default="fetched_at", pattern="^(score|fetched_at)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(ContentSource)
    count_query = select(func.count()).select_from(ContentSource)

    if source_type:
        query = query.where(ContentSource.source_type == source_type)
        count_query = count_query.where(ContentSource.source_type == source_type)

    # Sort
    sort_col = ContentSource.score if sort_by == "score" else ContentSource.fetched_at
    query = query.order_by(sort_col.desc() if sort_order == "desc" else sort_col.asc())

    # Count
    total = (await db.execute(count_query)).scalar_one()

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return ContentListResponse(
        items=[ContentSourceResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 0,
    )


@router.get("/{content_id}", response_model=ContentSourceResponse)
async def get_content(
    content_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    import uuid as _uuid

    try:
        uid = _uuid.UUID(content_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid content ID")

    result = await db.execute(select(ContentSource).where(ContentSource.id == uid))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Content not found")
    return item


@router.post("/{content_id}/generate", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def generate_post_from_content(
    content_id: str,
    data: GeneratePostRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    import uuid as _uuid

    try:
        uid = _uuid.UUID(content_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid content ID")

    generator = PostGenerator(db=db)
    try:
        post = await generator.generate_post(
            content_source_id=uid,
            target_platform=data.target_platform,
            content_type=data.content_type,
            tone=data.tone,
            user_id=user.id,
        )
        return post
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {e}")


@router.post("/refresh", status_code=status.HTTP_202_ACCEPTED)
async def refresh_content(_: User = Depends(get_current_user)):
    from app.tasks.research_tasks import fetch_trending_content

    task = fetch_trending_content.delay()
    return {"message": "Content refresh triggered", "task_id": str(task.id)}
