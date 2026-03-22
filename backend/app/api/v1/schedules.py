"""Schedule API routes - CRUD for recurring content generation schedules."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.schedule import Schedule
from app.models.user import User
from app.schemas.schedule import (
    CreateScheduleRequest,
    ScheduleListResponse,
    ScheduleResponse,
    UpdateScheduleRequest,
)

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.get("", response_model=ScheduleListResponse)
async def list_schedules(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Schedule).where(Schedule.user_id == user.id).order_by(Schedule.created_at.desc())
    )
    items = result.scalars().all()
    return ScheduleListResponse(
        items=[ScheduleResponse.model_validate(s) for s in items],
        total=len(items),
    )


@router.post("", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    data: CreateScheduleRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    schedule = Schedule(
        user_id=user.id,
        name=data.name,
        platform=data.platform,
        content_types=data.content_types,
        cron_expression=data.cron_expression,
        timezone=data.timezone,
        auto_approve=data.auto_approve,
    )
    db.add(schedule)
    await db.flush()
    await db.refresh(schedule)
    return schedule


@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        uid = uuid.UUID(schedule_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid schedule ID")

    result = await db.execute(
        select(Schedule).where(Schedule.id == uid, Schedule.user_id == user.id)
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: str,
    data: UpdateScheduleRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        uid = uuid.UUID(schedule_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid schedule ID")

    result = await db.execute(
        select(Schedule).where(Schedule.id == uid, Schedule.user_id == user.id)
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(schedule, field, value)

    await db.flush()
    await db.refresh(schedule)
    return schedule


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        uid = uuid.UUID(schedule_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid schedule ID")

    result = await db.execute(
        select(Schedule).where(Schedule.id == uid, Schedule.user_id == user.id)
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    await db.delete(schedule)
