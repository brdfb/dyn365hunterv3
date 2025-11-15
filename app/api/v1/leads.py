"""API v1 leads endpoints - Proxy to legacy handlers."""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.api.leads import (
    get_leads,
    get_lead,
    export_leads,
    enrich_lead,
    get_score_breakdown,
    LeadsListResponse,
    LeadResponse,
    EnrichLeadResponse,
    ScoreBreakdownResponse,
)
from app.db.session import get_db

router = APIRouter(prefix="/leads", tags=["leads", "v1"])


@router.get("", response_model=LeadsListResponse)
async def get_leads_v1(
    segment: Optional[str] = Query(
        None, description="Filter by segment (Migration, Existing, Cold, Skip)"
    ),
    min_score: Optional[int] = Query(
        None, ge=0, le=100, description="Minimum readiness score (0-100)"
    ),
    provider: Optional[str] = Query(
        None, description="Filter by provider (M365, Google, etc.)"
    ),
    favorite: Optional[bool] = Query(
        None,
        description="Filter by favorites (true = only favorites, false = all leads)",
    ),
    sort_by: Optional[str] = Query(
        None,
        description="Sort by field (domain, readiness_score, priority_score, segment, provider, scanned_at)",
    ),
    sort_order: Optional[str] = Query(
        "asc", pattern="^(asc|desc)$", description="Sort order (asc or desc)"
    ),
    page: Optional[int] = Query(1, ge=1, description="Page number (1-based)"),
    page_size: Optional[int] = Query(
        50, ge=1, le=200, description="Number of items per page (max 200)"
    ),
    search: Optional[str] = Query(
        None, description="Full-text search in domain, canonical_name, and provider"
    ),
    request: Request = None,
    db: Session = Depends(get_db),
):
    """V1 endpoint - Get filtered, sorted, and paginated list of leads."""
    return await get_leads(
        segment=segment,
        min_score=min_score,
        provider=provider,
        favorite=favorite,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
        search=search,
        request=request,
        db=db,
    )


@router.get("/{domain}", response_model=LeadResponse)
async def get_lead_v1(domain: str, db: Session = Depends(get_db)):
    """V1 endpoint - Get a single lead by domain."""
    return await get_lead(domain=domain, db=db)


@router.get("/export")
async def export_leads_v1(
    segment: Optional[str] = Query(
        None, description="Filter by segment (Migration, Existing, Cold, Skip)"
    ),
    min_score: Optional[int] = Query(
        None, ge=0, le=100, description="Minimum readiness score (0-100)"
    ),
    provider: Optional[str] = Query(
        None, description="Filter by provider (M365, Google, etc.)"
    ),
    format: str = Query(
        "csv", pattern="^(csv|xlsx)$", description="Export format (csv or xlsx)"
    ),
    db: Session = Depends(get_db),
):
    """V1 endpoint - Export leads to CSV or Excel format."""
    return await export_leads(
        segment=segment, min_score=min_score, provider=provider, format=format, db=db
    )


@router.post("/{domain}/enrich", response_model=EnrichLeadResponse, status_code=200)
async def enrich_lead_v1(domain: str, db: Session = Depends(get_db)):
    """V1 endpoint - Enrich a lead with contact information."""
    return await enrich_lead(domain=domain, db=db)


@router.get("/{domain}/score-breakdown", response_model=ScoreBreakdownResponse)
async def get_score_breakdown_v1(domain: str, db: Session = Depends(get_db)):
    """V1 endpoint - Get detailed score breakdown for a lead."""
    return await get_score_breakdown(domain=domain, db=db)

