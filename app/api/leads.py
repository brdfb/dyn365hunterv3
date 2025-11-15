"""Leads endpoints for querying analyzed domains."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import pandas as pd
import uuid
from app.db.session import get_db
from app.core.normalizer import normalize_domain
from app.core.priority import calculate_priority_score
from app.core.enrichment import enrich_company_data
from app.core.score_breakdown import calculate_score_breakdown
from app.db.models import Company, Favorite, DomainSignal


router = APIRouter(prefix="/leads", tags=["leads"])


class LeadResponse(BaseModel):
    """Response model for a single lead."""

    company_id: Optional[int] = None
    canonical_name: Optional[str] = None
    domain: str
    provider: Optional[str] = None
    country: Optional[str] = None
    contact_emails: Optional[List[str]] = None  # G16: Lead enrichment
    contact_quality_score: Optional[int] = None  # G16: Lead enrichment
    linkedin_pattern: Optional[str] = None  # G16: Lead enrichment
    spf: Optional[bool] = None
    dkim: Optional[bool] = None
    dmarc_policy: Optional[str] = None
    mx_root: Optional[str] = None
    registrar: Optional[str] = None
    expires_at: Optional[str] = None
    nameservers: Optional[List[str]] = None
    scan_status: Optional[str] = None
    scanned_at: Optional[str] = None
    readiness_score: Optional[int] = None
    segment: Optional[str] = None
    reason: Optional[str] = None
    priority_score: Optional[int] = None


class LeadsListResponse(BaseModel):
    """Response model for paginated leads list (G19)."""

    leads: List[LeadResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


@router.get("/export")
async def export_leads(
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
    """
    Export leads to CSV or Excel format.

    Uses the same filtering logic as GET /leads endpoint.
    Returns a downloadable file with lead data.

    Query parameters:
    - segment: Filter by segment (Migration, Existing, Cold, Skip)
    - min_score: Minimum readiness score (0-100)
    - provider: Filter by provider name
    - format: Export format (csv or xlsx, default: csv)

    Returns:
        CSV or Excel file download with lead data
    """
    # Build query using leads_ready VIEW (same as GET /leads)
    query = """
        SELECT 
            company_id,
            canonical_name,
            domain,
            provider,
            country,
            spf,
            dkim,
            dmarc_policy,
            mx_root,
            registrar,
            expires_at,
            nameservers,
            scan_status,
            scanned_at,
            readiness_score,
            segment,
            reason
        FROM leads_ready
        WHERE 1=1
    """

    params = {}

    # Add filters (same logic as GET /leads)
    if segment:
        query += " AND segment = :segment"
        params["segment"] = segment

    if min_score is not None:
        query += " AND readiness_score >= :min_score"
        params["min_score"] = min_score

    if provider:
        query += " AND provider = :provider"
        params["provider"] = provider

    # Only return leads that have been scanned (have a score)
    query += " AND readiness_score IS NOT NULL"

    # Note: We'll sort by priority_score in Python after calculating it
    query += " ORDER BY readiness_score DESC, domain ASC"

    try:
        result = db.execute(text(query), params)
        rows = result.fetchall()

        # Convert to list of dictionaries
        leads_data = []
        for row in rows:
            # Calculate priority score
            priority_score = calculate_priority_score(row.segment, row.readiness_score)

            lead_dict = {
                "domain": row.domain,
                "company_name": row.canonical_name or "",
                "provider": row.provider or "",
                "country": row.country or "",
                "segment": row.segment or "",
                "readiness_score": row.readiness_score or 0,
                "priority_score": priority_score or 6,
                "spf": "Yes" if row.spf else "No",
                "dkim": "Yes" if row.dkim else "No",
                "dmarc_policy": row.dmarc_policy or "None",
                "mx_root": row.mx_root or "",
                "registrar": row.registrar or "",
                "expires_at": str(row.expires_at) if row.expires_at else "",
                "nameservers": ", ".join(row.nameservers) if row.nameservers else "",
                "scan_status": row.scan_status or "",
                "scanned_at": str(row.scanned_at) if row.scanned_at else "",
                "reason": row.reason or "",
            }
            leads_data.append(lead_dict)

        # Sort by priority_score ASC (1 = highest priority), then readiness_score DESC
        leads_data.sort(
            key=lambda x: (x.get("priority_score", 999), -x.get("readiness_score", 0))
        )

        # Convert to DataFrame
        df = pd.DataFrame(leads_data)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        if format == "csv":
            # Generate CSV content
            csv_content = df.to_csv(index=False)

            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=leads_{timestamp}.csv",
                    "Content-Type": "text/csv; charset=utf-8",
                },
            )
        else:  # xlsx
            # Generate Excel content
            from io import BytesIO

            output = BytesIO()

            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Leads")

            output.seek(0)
            excel_content = output.read()

            return Response(
                content=excel_content,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": f"attachment; filename=leads_{timestamp}.xlsx"
                },
            )

    except Exception as e:
        from app.core.logging import logger
        logger.error("export_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"An error occurred while exporting leads: {str(e)}"
        )


def get_user_id(request: Request) -> str:
    """
    Get user ID from session (session-based, no auth yet).

    For now, we use a session cookie or generate a default user_id.
    In the future, this will be replaced with proper authentication.
    """
    # Try to get session ID from cookie
    session_id = request.cookies.get("session_id")

    if not session_id:
        # Generate a new session ID (for demo purposes)
        # In production, this should be handled by proper session management
        session_id = str(uuid.uuid4())

    return session_id


@router.get("", response_model=LeadsListResponse)
async def get_leads(
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
    # G19: UI upgrade - Sorting, pagination, search
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
    """
    Get filtered, sorted, and paginated list of leads (G19).

    Query parameters:
    - segment: Filter by segment (Migration, Existing, Cold, Skip)
    - min_score: Minimum readiness score (0-100)
    - provider: Filter by provider name
    - favorite: Filter by favorites (true = only favorites, false = all leads)
    - sort_by: Sort by field (domain, readiness_score, priority_score, segment, provider, scanned_at)
    - sort_order: Sort order (asc or desc, default: asc)
    - page: Page number (1-based, default: 1)
    - page_size: Number of items per page (default: 50, max: 200)
    - search: Full-text search in domain, canonical_name, and provider

    Returns:
        LeadsListResponse with paginated leads and metadata
    """
    # Build query using leads_ready VIEW
    query = """
        SELECT 
            company_id,
            canonical_name,
            domain,
            provider,
            country,
            spf,
            dkim,
            dmarc_policy,
            mx_root,
            registrar,
            expires_at,
            nameservers,
            scan_status,
            scanned_at,
            readiness_score,
            segment,
            reason
        FROM leads_ready
        WHERE 1=1
    """

    params = {}

    # Add filters
    if segment:
        query += " AND segment = :segment"
        params["segment"] = segment

    if min_score is not None:
        query += " AND readiness_score >= :min_score"
        params["min_score"] = min_score

    if provider:
        query += " AND provider = :provider"
        params["provider"] = provider

    # G19: Add search filter (full-text search in domain, canonical_name, provider)
    if search:
        search_pattern = f"%{search.lower()}%"
        query += """ AND (
            LOWER(domain) LIKE :search 
            OR LOWER(canonical_name) LIKE :search 
            OR LOWER(provider) LIKE :search
        )"""
        params["search"] = search_pattern

    # Only return leads that have been scanned (have a score)
    query += " AND readiness_score IS NOT NULL"

    # Note: We'll sort by priority_score in Python after calculating it
    # because priority_score is computed from segment + readiness_score
    # Default sorting (if sort_by not specified) is by priority_score
    query += " ORDER BY readiness_score DESC, domain ASC"

    try:
        result = db.execute(text(query), params)
        rows = result.fetchall()

        # Filter by favorites if requested
        if favorite is True:
            # Get user ID from session
            user_id = get_user_id(request) if request else "default"

            # Get favorite domains for this user
            favorite_domains = {
                fav.domain
                for fav in db.query(Favorite).filter(Favorite.user_id == user_id).all()
            }

            # Filter rows to only include favorite domains
            rows = [row for row in rows if row.domain in favorite_domains]

        leads = []
        for row in rows:
            # Calculate priority score
            priority_score = calculate_priority_score(row.segment, row.readiness_score)

            lead = LeadResponse(
                company_id=row.company_id,
                canonical_name=row.canonical_name,
                domain=row.domain,
                provider=row.provider,
                country=row.country,
                spf=row.spf,
                dkim=row.dkim,
                dmarc_policy=row.dmarc_policy,
                mx_root=row.mx_root,
                registrar=row.registrar,
                expires_at=str(row.expires_at) if row.expires_at else None,
                nameservers=row.nameservers,
                scan_status=row.scan_status,
                scanned_at=str(row.scanned_at) if row.scanned_at else None,
                readiness_score=row.readiness_score,
                segment=row.segment,
                reason=row.reason,
                priority_score=priority_score,
            )
            leads.append(lead)

        # G19: Apply sorting
        # Default: priority_score ASC (1 = highest priority), then readiness_score DESC
        if sort_by:
            # Map sort_by field names to sort keys
            sort_key_map = {
                "domain": lambda x: (x.domain or "",),
                "readiness_score": lambda x: (
                    x.readiness_score if x.readiness_score is not None else -1,
                ),
                "priority_score": lambda x: (
                    x.priority_score if x.priority_score is not None else 999,
                ),
                "segment": lambda x: (x.segment or "",),
                "provider": lambda x: (x.provider or "",),
                "scanned_at": lambda x: (
                    x.scanned_at if x.scanned_at else "",
                ),
            }

            if sort_by in sort_key_map:
                reverse = sort_order == "desc"
                leads.sort(key=sort_key_map[sort_by], reverse=reverse)
            else:
                # Invalid sort_by, use default sorting
                leads.sort(
                    key=lambda x: (
                        x.priority_score if x.priority_score is not None else 999,
                        -(x.readiness_score if x.readiness_score is not None else 0),
                    )
                )
        else:
            # Default sorting: priority_score ASC, then readiness_score DESC
            leads.sort(
                key=lambda x: (
                    x.priority_score if x.priority_score is not None else 999,
                    -(x.readiness_score if x.readiness_score is not None else 0),
                )
            )

        # G19: Apply pagination
        total = len(leads)
        total_pages = (total + page_size - 1) // page_size  # Ceiling division
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_leads = leads[start_idx:end_idx]

        return LeadsListResponse(
            leads=paginated_leads,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{domain}", response_model=LeadResponse)
async def get_lead(domain: str, db: Session = Depends(get_db)):
    """
    Get a single lead by domain.

    Args:
        domain: Domain name (will be normalized)
        db: Database session

    Returns:
        LeadResponse with full lead details

    Raises:
        404: If domain not found or not scanned
    """
    # Normalize domain
    normalized_domain = normalize_domain(domain)

    if not normalized_domain:
        raise HTTPException(status_code=400, detail="Invalid domain format")

    # Query using direct JOIN (more reliable than VIEW)
    query = """
        SELECT 
            c.id AS company_id,
            c.canonical_name,
            c.domain,
            c.provider,
            c.country,
            c.contact_emails,
            c.contact_quality_score,
            c.linkedin_pattern,
            ds.spf,
            ds.dkim,
            ds.dmarc_policy,
            ds.mx_root,
            ds.registrar,
            ds.expires_at,
            ds.nameservers,
            ds.scan_status,
            ds.scanned_at,
            ls.readiness_score,
            ls.segment,
            ls.reason
        FROM companies c
        LEFT JOIN domain_signals ds ON c.domain = ds.domain
        LEFT JOIN lead_scores ls ON c.domain = ls.domain
        WHERE c.domain = :domain
    """

    try:
        result = db.execute(text(query), {"domain": normalized_domain})
        row = result.fetchone()

        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"Domain {normalized_domain} not found. Please ingest the domain first using /ingest/domain",
            )

        # Check if domain has been scanned
        if row.readiness_score is None:
            raise HTTPException(
                status_code=404,
                detail=f"Domain {normalized_domain} has not been scanned yet. Please use /scan/domain first.",
            )

        # Calculate priority score
        priority_score = calculate_priority_score(row.segment, row.readiness_score)

        # Convert contact_emails from JSONB to list if present
        contact_emails = None
        if row.contact_emails:
            if isinstance(row.contact_emails, list):
                contact_emails = row.contact_emails
            else:
                # Handle case where it might be stored differently
                contact_emails = (
                    list(row.contact_emails) if row.contact_emails else None
                )

        return LeadResponse(
            company_id=row.company_id,
            canonical_name=row.canonical_name,
            domain=row.domain,
            provider=row.provider,
            country=row.country,
            contact_emails=contact_emails,
            contact_quality_score=row.contact_quality_score,
            linkedin_pattern=row.linkedin_pattern,
            spf=row.spf,
            dkim=row.dkim,
            dmarc_policy=row.dmarc_policy,
            mx_root=row.mx_root,
            registrar=row.registrar,
            expires_at=str(row.expires_at) if row.expires_at else None,
            nameservers=row.nameservers,
            scan_status=row.scan_status,
            scanned_at=str(row.scanned_at) if row.scanned_at else None,
            readiness_score=row.readiness_score,
            segment=row.segment,
            reason=row.reason,
            priority_score=priority_score,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


class EnrichLeadRequest(BaseModel):
    """Request model for manual lead enrichment."""

    contact_emails: List[str] = Field(
        ..., description="List of contact email addresses"
    )


class EnrichLeadResponse(BaseModel):
    """Response model for lead enrichment."""

    domain: str
    contact_emails: List[str]
    contact_quality_score: int
    linkedin_pattern: Optional[str]
    message: str


@router.post("/{domain}/enrich", response_model=EnrichLeadResponse, status_code=200)
async def enrich_lead(
    domain: str, request: EnrichLeadRequest, db: Session = Depends(get_db)
):
    """
    Manually enrich a lead with contact emails.

    - Updates company record with enrichment data
    - Calculates contact quality score
    - Detects LinkedIn email pattern

    Args:
        domain: Domain name (will be normalized)
        request: Enrichment request with contact emails
        db: Database session

    Returns:
        EnrichLeadResponse with enrichment results

    Raises:
        404: If domain not found
        400: If domain is invalid or no emails provided
        500: If internal server error
    """
    # Normalize domain
    normalized_domain = normalize_domain(domain)

    if not normalized_domain:
        raise HTTPException(status_code=400, detail="Invalid domain format")

    # Validate contact emails
    if not request.contact_emails:
        raise HTTPException(
            status_code=400, detail="At least one contact email is required"
        )

    # Find company
    company = db.query(Company).filter(Company.domain == normalized_domain).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail=f"Domain {normalized_domain} not found. Please ingest the domain first using /ingest/domain",
        )

    try:
        # Enrich company data
        enrichment_data = enrich_company_data(
            emails=request.contact_emails, domain=normalized_domain
        )

        # Update company with enrichment data
        company.contact_emails = enrichment_data["contact_emails"]
        company.contact_quality_score = enrichment_data["contact_quality_score"]
        company.linkedin_pattern = enrichment_data["linkedin_pattern"]
        db.commit()
        db.refresh(company)

        return EnrichLeadResponse(
            domain=normalized_domain,
            contact_emails=enrichment_data["contact_emails"],
            contact_quality_score=enrichment_data["contact_quality_score"],
            linkedin_pattern=enrichment_data["linkedin_pattern"],
            message=f"Domain {normalized_domain} enriched successfully",
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


class ScoreBreakdownResponse(BaseModel):
    """Response model for score breakdown (G19)."""

    base_score: int
    provider: Dict[str, Any]  # {"name": str, "points": int}
    signal_points: Dict[str, int]  # {"spf": int, "dkim": int, "dmarc_*": int}
    risk_points: Dict[str, int]  # {"no_spf": int, "no_dkim": int, ...}
    total_score: int


@router.get("/{domain}/score-breakdown", response_model=ScoreBreakdownResponse)
async def get_score_breakdown(domain: str, db: Session = Depends(get_db)):
    """
    Get detailed score breakdown for a domain (G19).

    Args:
        domain: Domain name (will be normalized)
        db: Database session

    Returns:
        ScoreBreakdownResponse with detailed score components

    Raises:
        404: If domain not found or not scanned
    """
    # Normalize domain
    normalized_domain = normalize_domain(domain)

    if not normalized_domain:
        raise HTTPException(status_code=400, detail="Invalid domain format")

    # Get domain data
    company = db.query(Company).filter(Company.domain == normalized_domain).first()
    if not company:
        raise HTTPException(
            status_code=404,
            detail=f"Domain {normalized_domain} not found. Please ingest the domain first using /ingest/domain",
        )

    # Get domain signals
    domain_signal = (
        db.query(DomainSignal).filter(DomainSignal.domain == normalized_domain).first()
    )

    if not domain_signal or domain_signal.scan_status != "completed":
        raise HTTPException(
            status_code=404,
            detail=f"Domain {normalized_domain} has not been scanned yet. Please use /scan/domain first.",
        )

    # Prepare signals dictionary
    signals = {
        "spf": domain_signal.spf,
        "dkim": domain_signal.dkim,
        "dmarc_policy": domain_signal.dmarc_policy,
        "spf_record": getattr(domain_signal, "spf_record", None),  # Optional, for risk analysis (may not exist in model)
    }

    # Get MX records (if available)
    mx_records = None
    mx_records_attr = getattr(domain_signal, "mx_records", None)
    if mx_records_attr:
        if isinstance(mx_records_attr, list):
            mx_records = mx_records_attr
        else:
            # Handle case where it might be stored differently
            mx_records = list(mx_records_attr) if mx_records_attr else None

    # Calculate score breakdown
    breakdown = calculate_score_breakdown(
        provider=company.provider or "Unknown",
        signals=signals,
        mx_records=mx_records,
    )

    return ScoreBreakdownResponse(**breakdown.to_dict())
