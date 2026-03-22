"""Leads API routes - list, detail, update, delete, export, stats."""

import csv
import io
import math
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.api.deps import get_current_user
from app.database import get_db
from app.models.lead import LinkedInLead
from app.models.user import User
from app.schemas.lead import (
    LeadListResponse,
    LeadResponse,
    LeadStatsResponse,
    UpdateLeadRequest,
)

router = APIRouter(prefix="/leads", tags=["leads"])


def _user_leads_base(user: User):
    """Base query scoped to current user's leads."""
    return select(LinkedInLead).where(LinkedInLead.user_id == user.id)


@router.get("", response_model=LeadListResponse)
async def list_leads(
    search: str | None = Query(default=None),
    ai_status: str | None = Query(default=None),
    tag: str | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    base = _user_leads_base(user)
    count_q = select(func.count()).select_from(LinkedInLead).where(
        LinkedInLead.user_id == user.id
    )

    # Filters
    if search:
        pattern = f"%{search}%"
        base = base.where(
            LinkedInLead.name.ilike(pattern)
            | LinkedInLead.headline.ilike(pattern)
            | LinkedInLead.current_company.ilike(pattern)
        )
        count_q = count_q.where(
            LinkedInLead.name.ilike(pattern)
            | LinkedInLead.headline.ilike(pattern)
            | LinkedInLead.current_company.ilike(pattern)
        )
    if ai_status:
        base = base.where(LinkedInLead.ai_status == ai_status)
        count_q = count_q.where(LinkedInLead.ai_status == ai_status)
    if tag:
        base = base.where(LinkedInLead.tags.any(tag))
        count_q = count_q.where(LinkedInLead.tags.any(tag))

    total = (await db.execute(count_q)).scalar_one()

    # Sorting
    sort_col = getattr(LinkedInLead, sort_by, LinkedInLead.created_at)
    order = sort_col.desc() if sort_order == "desc" else sort_col.asc()

    query = (
        base.options(joinedload(LinkedInLead.engagements))
        .order_by(order)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    items = result.unique().scalars().all()

    return LeadListResponse(
        items=[LeadResponse.model_validate(lead) for lead in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 0,
    )


@router.get("/stats", response_model=LeadStatsResponse)
async def lead_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    base = select(func.count()).select_from(LinkedInLead).where(
        LinkedInLead.user_id == user.id
    )
    total = (await db.execute(base)).scalar_one()

    open_to_work = (
        await db.execute(base.where(LinkedInLead.ai_status == "OPEN_TO_WORK"))
    ).scalar_one()
    hiring = (
        await db.execute(base.where(LinkedInLead.ai_status == "HIRING"))
    ).scalar_one()
    has_email = (
        await db.execute(base.where(LinkedInLead.email.isnot(None)))
    ).scalar_one()

    return LeadStatsResponse(
        total_leads=total,
        open_to_work=open_to_work,
        hiring=hiring,
        has_email=has_email,
    )


@router.get("/export")
async def export_leads_csv(
    ai_status: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Export leads as CSV file."""
    base = _user_leads_base(user)
    if ai_status:
        base = base.where(LinkedInLead.ai_status == ai_status)

    result = await db.execute(base.order_by(LinkedInLead.created_at.desc()))
    leads = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Name", "Headline", "Company", "Email", "Location",
        "Industry", "Status", "Profile URL", "Tags", "Notes",
    ])

    for lead in leads:
        writer.writerow([
            lead.name or "",
            lead.headline or "",
            lead.current_company or "",
            lead.email or "",
            lead.location or "",
            lead.industry or "",
            lead.ai_status or "",
            lead.profile_url or "",
            ", ".join(lead.tags) if lead.tags else "",
            lead.notes or "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads.csv"},
    )


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        lid = uuid.UUID(lead_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid lead ID")

    result = await db.execute(
        _user_leads_base(user)
        .where(LinkedInLead.id == lid)
        .options(joinedload(LinkedInLead.engagements))
    )
    lead = result.unique().scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    data: UpdateLeadRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        lid = uuid.UUID(lead_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid lead ID")

    result = await db.execute(
        _user_leads_base(user).where(LinkedInLead.id == lid)
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(lead, key, value)

    await db.commit()
    await db.refresh(lead)
    return lead


@router.delete("/{lead_id}", status_code=204)
async def delete_lead(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        lid = uuid.UUID(lead_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid lead ID")

    result = await db.execute(
        _user_leads_base(user).where(LinkedInLead.id == lid)
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    await db.delete(lead)
    await db.commit()
