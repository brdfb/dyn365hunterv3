"""Partner Center referrals endpoints (Phase 2)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from pydantic import BaseModel
from typing import List, Optional
from app.db.session import get_db
from app.db.models import PartnerCenterReferral, Company, RawLead
from app.config import settings
from app.core.logging import logger
from app.core.referral_ingestion import sync_referrals_from_partner_center, update_existing_referral_types
from app.core.tasks import sync_partner_center_referrals_task
from app.core.normalizer import normalize_domain
from app.core.merger import upsert_companies
from app.schemas.referrals import (
    ReferralInboxItem,
    ReferralInboxResponse,
    LinkReferralRequest,
    LinkReferralResponse,
    CreateLeadFromReferralRequest,
    CreateLeadFromReferralResponse,
    ReferralDetailResponse,
)


router = APIRouter(prefix="/api/v1/partner-center/referrals", tags=["referrals", "partner-center"])


class SyncReferralsRequest(BaseModel):
    """Request model for manual referral sync."""

    force: bool = False  # Force sync even if recently synced (future enhancement)


class SyncReferralsResponse(BaseModel):
    """Response model for referral sync operation."""

    success: bool
    message: str
    enqueued: bool = False  # Task enqueued successfully
    task_id: Optional[str] = None  # Celery task ID for monitoring/debugging
    success_count: int = 0  # Will be 0 initially (task runs async)
    failure_count: int = 0  # Will be 0 initially (task runs async)
    skipped_count: int = 0  # Will be 0 initially (task runs async)
    errors: List[str] = []


@router.post("/sync", response_model=SyncReferralsResponse)
async def sync_referrals(
    request: Optional[SyncReferralsRequest] = None,
    db: Session = Depends(get_db),
):
    """
    Manually sync referrals from Partner Center.

    **Note**: This is an internal/admin-only endpoint. Not intended for public API consumers.

    This endpoint:
    - Fetches referrals from Partner Center API
    - Normalizes domains from referrals
    - Upserts companies with Azure Tenant ID override
    - Triggers domain scans (idempotent - domain-based)
    - Tracks referral lifecycle in partner_center_referrals table

    **MVP**: This endpoint triggers async Celery task for long-running operation.
    Sync results are logged. Use `task_id` to monitor task execution.

    Args:
        request: Optional sync request (force flag for future enhancement)
        db: Database session

    Returns:
        SyncReferralsResponse with task_id and sync status

    Raises:
        400: If Partner Center integration is disabled (feature flag OFF)
        500: If sync operation fails
    """
    # Feature flag check
    if not settings.partner_center_enabled:
        raise HTTPException(
            status_code=400,
            detail="Partner Center integration is disabled. Enable feature flag to use this endpoint.",
        )

    try:
        # Trigger async Celery task for long-running sync operation
        # Task will handle sync_referrals_from_partner_center() execution
        task_result = sync_partner_center_referrals_task.delay()

        logger.info(
            "partner_center_sync_triggered",
            task_id=task_result.id,
            feature_flag_enabled=settings.partner_center_enabled,
        )

        # Return immediate response (task runs async)
        return SyncReferralsResponse(
            success=True,
            message="Referral sync task enqueued. Check logs for results.",
            enqueued=True,
            task_id=task_result.id,
            success_count=0,  # Will be updated by task (check logs)
            failure_count=0,
            skipped_count=0,
            errors=[],
        )

    except Exception as e:
        logger.error(
            "partner_center_sync_error",
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start referral sync: {str(e)}",
        )


@router.get("/inbox", response_model=ReferralInboxResponse)
async def get_referral_inbox(
    link_status: Optional[str] = Query(None, description="Filter by link_status (auto_linked, unlinked)"),
    referral_type: Optional[str] = Query(None, description="Filter by referral_type (co-sell, marketplace, solution-provider)"),
    status: Optional[str] = Query(None, description="Filter by status (Active, New, etc.)"),
    search: Optional[str] = Query(None, description="Free text search in company_name, customer_name, domain, raw_domain"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(50, ge=1, le=200, description="Number of items per page (max 200)"),
    db: Session = Depends(get_db),
):
    """
    Get Partner Center referrals inbox (all referrals, linked or unlinked).
    
    Phase 2: Referral Inbox endpoint for managing all Partner Center referrals.
    
    Query parameters:
    - link_status: Filter by link status (auto_linked, unlinked)
    - referral_type: Filter by referral type (co-sell, marketplace, solution-provider)
    - status: Filter by Partner Center status (Active, New, etc.)
    - search: Free text search in company_name, customer_name, domain, raw_domain
    - page: Page number (default: 1)
    - page_size: Items per page (default: 50, max: 200)
    
    Returns:
        ReferralInboxResponse with paginated referrals list
    """
    query = db.query(PartnerCenterReferral)
    
    # Apply filters
    if link_status:
        query = query.filter(PartnerCenterReferral.link_status == link_status)
    
    if referral_type:
        query = query.filter(PartnerCenterReferral.referral_type == referral_type)
    
    if status:
        query = query.filter(PartnerCenterReferral.status == status)
    
    if search:
        # Free text search in multiple fields
        like = f"%{search.lower()}%"
        query = query.filter(
            or_(
                func.lower(PartnerCenterReferral.company_name).like(like),
                func.lower(PartnerCenterReferral.customer_name).like(like),
                func.lower(PartnerCenterReferral.domain).like(like),
                func.lower(PartnerCenterReferral.raw_domain).like(like),
            )
        )
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination and ordering
    referrals = (
        query.order_by(PartnerCenterReferral.synced_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    
    # Convert to response model
    return ReferralInboxResponse(
        referrals=[
            ReferralInboxItem(
                id=r.id,
                referral_id=r.referral_id,
                company_name=r.company_name,
                customer_name=r.customer_name,
                domain=r.domain,
                raw_domain=r.raw_domain,
                referral_type=r.referral_type,
                status=r.status,
                substatus=r.substatus,
                link_status=r.link_status,
                linked_lead_id=r.linked_lead_id,
                deal_value=float(r.deal_value) if r.deal_value else None,
                currency=r.currency,
                synced_at=r.synced_at.isoformat() if r.synced_at else None,
            )
            for r in referrals
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/{referral_id}/link", response_model=LinkReferralResponse)
async def link_referral_to_lead(
    referral_id: str,
    payload: LinkReferralRequest,
    db: Session = Depends(get_db),
):
    """
    Link unlinked referral to existing lead by domain.
    
    Phase 2: Link action - connects a referral to an existing Hunter lead.
    
    Args:
        referral_id: Partner Center referral ID
        payload: Link request with lead_domain
        db: Database session
        
    Returns:
        LinkReferralResponse with link status and lead info
        
    Raises:
        404: If referral or lead not found
        400: If domain is invalid
    """
    # Find referral
    referral = (
        db.query(PartnerCenterReferral)
        .filter(PartnerCenterReferral.referral_id == referral_id)
        .first()
    )
    
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")
    
    # Normalize domain
    normalized_domain = normalize_domain(payload.lead_domain)
    if not normalized_domain:
        raise HTTPException(status_code=400, detail="Invalid domain format")
    
    # Find company (lead)
    company = (
        db.query(Company)
        .filter(Company.domain == normalized_domain)
        .first()
    )
    
    if not company:
        raise HTTPException(
            status_code=404,
            detail=f"Lead not found for domain: {normalized_domain}",
        )
    
    # Update referral link
    referral.link_status = "auto_linked"
    referral.linked_lead_id = company.id
    referral.domain = normalized_domain  # Update domain if was NULL
    
    db.commit()
    db.refresh(referral)
    
    logger.info(
        "partner_center_referral_linked",
        referral_id=referral_id,
        lead_id=company.id,
        domain=normalized_domain,
    )
    
    return LinkReferralResponse(
        status="linked",
        lead_id=company.id,
        domain=normalized_domain,
    )


@router.post("/{referral_id}/create-lead", response_model=CreateLeadFromReferralResponse)
async def create_lead_from_referral(
    referral_id: str,
    payload: CreateLeadFromReferralRequest,
    db: Session = Depends(get_db),
):
    """
    Create Hunter lead from unlinked referral.
    
    Phase 2: Create lead action - creates a new Hunter lead from referral domain.
    
    Args:
        referral_id: Partner Center referral ID
        payload: Create lead request (optional company_name_override, notes)
        db: Database session
        
    Returns:
        CreateLeadFromReferralResponse with created lead info
        
    Raises:
        404: If referral not found
        400: If referral has no domain
    """
    # Find referral
    referral = (
        db.query(PartnerCenterReferral)
        .filter(PartnerCenterReferral.referral_id == referral_id)
        .first()
    )
    
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")
    
    # Check if referral has domain
    if not referral.domain:
        raise HTTPException(
            status_code=400,
            detail="Referral has no normalized domain; cannot create lead",
        )
    
    # Determine company name (override > referral.company_name > referral.customer_name > domain)
    company_name = (
        payload.company_name_override
        or referral.company_name
        or referral.customer_name
        or referral.domain
    )
    
    # Create/upsert company using existing merger utility
    company = upsert_companies(
        db=db,
        domain=referral.domain,
        company_name=company_name,
    )
    
    # Create raw_lead record (following existing pattern)
    raw_lead = RawLead(
        source="partner_center_referral",
        company_name=company_name,
        domain=referral.domain,
        payload={
            "referral_id": referral.referral_id,
            "referral_type": referral.referral_type,
            "notes": payload.notes,
            "created_from": "referral_inbox",
        },
    )
    db.add(raw_lead)
    db.commit()
    db.refresh(raw_lead)
    
    # Update referral link
    referral.link_status = "auto_linked"
    referral.linked_lead_id = company.id
    db.commit()
    db.refresh(referral)
    
    logger.info(
        "partner_center_referral_lead_created",
        referral_id=referral_id,
        lead_id=company.id,
        domain=company.domain,
        company_name=company_name,
    )
    
    return CreateLeadFromReferralResponse(
        status="created",
        lead_id=company.id,
        domain=company.domain,
    )


@router.get("/{referral_id}", response_model=ReferralDetailResponse)
async def get_referral_detail(
    referral_id: str,
    include_raw: bool = Query(
        False, description="Include raw Partner Center payload for debugging", alias="include_raw"
    ),
    db: Session = Depends(get_db),
):
    """
    Get full detail for a Partner Center referral (for modal view).

    Returns structured summary (status, contact, deal) + optional raw JSON.
    """
    if not settings.partner_center_enabled:
        raise HTTPException(
            status_code=400,
            detail="Partner Center integration is disabled. Enable feature flag to use this endpoint.",
        )

    referral = (
        db.query(PartnerCenterReferral)
        .filter(PartnerCenterReferral.referral_id == referral_id)
        .first()
    )

    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")

    raw_data = referral.raw_data or {}
    customer_profile = raw_data.get("customerProfile") or {}
    details_data = raw_data.get("details") or {}
    
    # Try multiple locations for contact info (Partner Center API structure varies)
    # 1. Top-level contact
    contact_data = raw_data.get("contact") or {}
    # 2. Details.contact (some referral types)
    if not contact_data.get("email") and not contact_data.get("name"):
        contact_data = details_data.get("contact") or contact_data
    # 3. CustomerProfile.primaryContact (if exists)
    if not contact_data.get("email") and not contact_data.get("name"):
        contact_data = customer_profile.get("primaryContact") or contact_data

    def _full_name(obj: dict) -> Optional[str]:
        name = obj.get("name")
        if name:
            return name
        first = obj.get("firstName") or ""
        last = obj.get("lastName") or ""
        full = f"{first} {last}".strip()
        return full if full else None

    # Extract contact info (primary contact from lead's organization)
    # Note: contact is the primary contact person from the customer's organization
    contact_info = {
        "name": _full_name(contact_data),
        "email": contact_data.get("email"),
        "phone": contact_data.get("phoneNumber") or contact_data.get("phone"),
        "title": contact_data.get("jobTitle") or contact_data.get("title"),
    }
    
    # Extract team members (customer's team from customerProfile.team)
    # Note: customerProfile.team = customer's organization team members (not Microsoft partner team)
    # These are additional people from the customer's organization, not the primary contact
    team_members = []
    for member in customer_profile.get("team") or []:
        team_members.append(
            {
                "name": _full_name(member),
                "email": member.get("email"),
                "role": member.get("role") or member.get("title"),
                "phone": member.get("phoneNumber"),
            }
        )
    
    # Fallback: If contact is completely empty but we have team members,
    # use first team member as primary contact (practical fallback)
    # This is a pragmatic solution since Partner Center API often doesn't provide contact info
    # In practice, if contact is empty, the first team member is likely the primary contact
    if not contact_info["name"] and not contact_info["email"] and team_members:
        first_member = team_members[0]
        contact_info = {
            "name": first_member.get("name"),
            "email": first_member.get("email"),
            "phone": first_member.get("phone"),
            "title": first_member.get("role"),
        }
        # Remove first member from team list to avoid duplication
        # (since we're using it as primary contact)
        team_members = team_members[1:]

    deal_info = {
        "lead_name": details_data.get("leadName") or raw_data.get("name"),
        "lead_id": raw_data.get("leadId") or details_data.get("leadId"),
        "estimated_close_date": details_data.get("estimatedCloseDate"),
        "estimated_value": None,
        "currency": details_data.get("currency") or referral.currency,
        "notes": details_data.get("notes") or raw_data.get("notes"),
    }

    estimated_value = details_data.get("estimatedValue")
    if estimated_value is not None:
        try:
            deal_info["estimated_value"] = float(estimated_value)
        except (TypeError, ValueError):
            deal_info["estimated_value"] = estimated_value
    elif referral.deal_value is not None:
        deal_info["estimated_value"] = float(referral.deal_value)

    organization_size = customer_profile.get("organizationSize")
    if not organization_size:
        organization_size = raw_data.get("organizationSize")

    customer_country = (customer_profile.get("address") or {}).get("country")

    response = ReferralDetailResponse(
        referral_id=referral.referral_id,
        referral_type=referral.referral_type,
        status=referral.status,
        substatus=referral.substatus,
        direction=referral.direction,
        link_status=referral.link_status,
        company_name=referral.company_name,
        customer_name=referral.customer_name,
        customer_country=customer_country,
        organization_size=organization_size,
        domain=referral.domain,
        raw_domain=referral.raw_domain,
        deal_value=float(referral.deal_value) if referral.deal_value else None,
        currency=referral.currency,
        synced_at=referral.synced_at.isoformat() if referral.synced_at else None,
        contact=contact_info,
        deal=deal_info,
        team_members=team_members,
        raw_data=raw_data if include_raw else None,
    )

    return response

