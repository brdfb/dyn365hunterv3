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
from app.core.enrichment_service import build_infra_summary
from app.db.models import Company, Favorite, DomainSignal, LeadScore
from app.config import settings


router = APIRouter(prefix="/leads", tags=["leads"])


class LeadResponse(BaseModel):
    """Response model for a single lead."""

    company_id: Optional[int] = None
    canonical_name: Optional[str] = None
    domain: str
    provider: Optional[str] = None
    tenant_size: Optional[str] = None  # G20: Tenant size (small/medium/large)
    local_provider: Optional[str] = None  # G20: Local provider name (e.g., TürkHost)
    country: Optional[str] = None
    contact_emails: Optional[List[str]] = None  # G16: Lead enrichment
    contact_quality_score: Optional[int] = None  # G16: Lead enrichment
    linkedin_pattern: Optional[str] = None  # G16: Lead enrichment
    spf: Optional[bool] = None
    dkim: Optional[bool] = None
    dmarc_policy: Optional[str] = None
    dmarc_coverage: Optional[int] = None  # G20: DMARC coverage (0-100)
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
    # CSP P-Model fields (Phase 2)
    technical_heat: Optional[str] = None  # 'Hot', 'Warm', 'Cold'
    commercial_segment: Optional[str] = None  # 'GREENFIELD', 'COMPETITIVE', 'WEAK_PARTNER', 'RENEWAL', 'LOW_INTENT', 'NO_GO'
    commercial_heat: Optional[str] = None  # 'HIGH', 'MEDIUM', 'LOW'
    priority_category: Optional[str] = None  # 'P1', 'P2', 'P3', 'P4', 'P5', 'P6'
    priority_label: Optional[str] = None  # Human-readable label (e.g., 'High Potential Greenfield')
    infrastructure_summary: Optional[str] = None  # IP enrichment summary (Level 1)
    referral_type: Optional[str] = None  # Partner Center referral type ('co-sell', 'marketplace', 'solution-provider')
    link_status: Optional[str] = None  # Partner Center link status ('linked', 'unlinked', 'mixed') - mixed when multiple referrals with different statuses
    referral_id: Optional[str] = None  # Partner Center referral ID (primary referral if multiple exist)
    # Solution 2: Multiple referrals aggregate (MVP)
    referral_count: int = 0  # Total number of referrals for this domain
    referral_types: List[str] = []  # Array of distinct referral types (e.g., ["co-sell", "marketplace"])
    referral_ids: List[str] = []  # Array of referral IDs sorted by priority (most recent first)
    # D365 Integration fields (Phase 3)
    d365_sync_status: Optional[str] = None  # 'not_synced', 'queued', 'in_progress', 'synced', 'error'
    d365_sync_last_at: Optional[str] = None  # Last sync timestamp (ISO format)
    d365_lead_id: Optional[str] = None  # D365 Lead ID (for generating link)
    d365_lead_url: Optional[str] = None  # D365 Lead URL (generated from base_url + lead_id)


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
    referral_type: Optional[str] = Query(
        None, description="Filter by Partner Center referral type (co-sell, marketplace, solution-provider)"
    ),
    search: Optional[str] = Query(
        None, description="Full-text search in domain, canonical_name, and provider"
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
    # Build query using leads_ready VIEW with LEFT JOIN to partner_center_referrals (same as GET /leads)
    # Use DISTINCT ON (domain) to prevent duplicates when there are multiple domain_signals or lead_scores
    # LEFT JOIN partner_center_referrals to get referral_type (Task 2.5)
    # Aggregate link_status for multiple referrals: if all same, use it; otherwise 'mixed'
    query = """
        SELECT DISTINCT ON (lr.domain)
            lr.company_id,
            lr.canonical_name,
            lr.domain,
            lr.provider,
            lr.tenant_size,
            lr.local_provider,
            lr.country,
            lr.spf,
            lr.dkim,
            lr.dmarc_policy,
            lr.dmarc_coverage,
            lr.mx_root,
            lr.registrar,
            lr.expires_at,
            lr.nameservers,
            lr.scan_status,
            lr.scanned_at,
            lr.readiness_score,
            lr.segment,
            lr.reason,
            lr.technical_heat,
            lr.commercial_segment,
            lr.commercial_heat,
            lr.priority_category,
            lr.priority_label,
            MAX(pcr.referral_type) AS referral_type,
            -- Calculate aggregated link_status: normalize NULL to 'none' when no referrals, 'unlinked' when referral exists but status is NULL
            -- Also normalize 'auto_linked' to 'linked' for consistency
            CASE 
                WHEN COUNT(pcr.id) = 0 THEN 'none'
                WHEN COUNT(DISTINCT COALESCE(
                    CASE WHEN pcr.link_status = 'auto_linked' THEN 'linked' ELSE pcr.link_status END, 
                    'unlinked'
                )) = 1 
                     THEN MIN(COALESCE(
                         CASE WHEN pcr.link_status = 'auto_linked' THEN 'linked' ELSE pcr.link_status END,
                         'unlinked'
                     ))
                ELSE 'mixed'
            END AS aggregated_link_status,
            -- Get primary referral_id: deterministic ordering (most recent referral first)
            COALESCE(
                (SELECT pcr_inner.referral_id 
                 FROM partner_center_referrals pcr_inner 
                 WHERE pcr_inner.domain = lr.domain 
                 ORDER BY pcr_inner.synced_at DESC, pcr_inner.created_at DESC 
                 LIMIT 1),
                NULL
            ) AS primary_referral_id,
            -- Solution 2: Multiple referrals aggregate (MVP)
            COUNT(pcr.id) AS referral_count,
            ARRAY_AGG(DISTINCT pcr.referral_type) FILTER (WHERE pcr.referral_type IS NOT NULL) AS referral_types,
            ARRAY_AGG(pcr.referral_id ORDER BY pcr.synced_at DESC, pcr.created_at DESC) 
                FILTER (WHERE pcr.referral_id IS NOT NULL) AS referral_ids
        FROM leads_ready lr
        LEFT JOIN partner_center_referrals pcr ON lr.domain = pcr.domain
        WHERE 1=1
    """

    params = {}

    # Add filters (same logic as GET /leads)
    if segment:
        query += " AND lr.segment = :segment"
        params["segment"] = segment

    if min_score is not None:
        query += " AND lr.readiness_score >= :min_score"
        params["min_score"] = min_score

    if provider:
        query += " AND lr.provider = :provider"
        params["provider"] = provider

    # Partner Center referral type filter
    if referral_type:
        query += " AND pcr.referral_type = :referral_type"
        params["referral_type"] = referral_type

    # G19: Add search filter (full-text search in domain, canonical_name, provider)
    if search:
        search_pattern = f"%{search.lower()}%"
        query += """ AND (
            LOWER(lr.domain) LIKE :search 
            OR LOWER(lr.canonical_name) LIKE :search 
            OR LOWER(lr.provider) LIKE :search
        )"""
        params["search"] = search_pattern

    # Only return leads that have been scanned (have a score)
    query += " AND lr.readiness_score IS NOT NULL"

    # GROUP BY is needed for aggregate functions (aggregated_link_status, primary_referral_id)
    query += " GROUP BY lr.company_id, lr.canonical_name, lr.domain, lr.provider, lr.tenant_size, lr.local_provider, lr.country, lr.spf, lr.dkim, lr.dmarc_policy, lr.dmarc_coverage, lr.mx_root, lr.registrar, lr.expires_at, lr.nameservers, lr.scan_status, lr.scanned_at, lr.readiness_score, lr.segment, lr.reason, lr.technical_heat, lr.commercial_segment, lr.commercial_heat, lr.priority_category, lr.priority_label"
    # Note: DISTINCT ON requires domain to be first in ORDER BY
    # We'll sort by priority_score in Python after calculating it
    query += " ORDER BY lr.domain, lr.scanned_at DESC NULLS LAST"

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
                "priority_score": priority_score or 7,
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
                "referral_type": getattr(row, "referral_type", None) or "",  # Task 2.5: Partner Center referral type
                "link_status": getattr(row, "aggregated_link_status", None) or "none",  # Partner Center link status (linked/unlinked/mixed/none)
                # Solution 2: Multiple referrals aggregate (MVP)
                "referral_count": getattr(row, "referral_count", 0) or 0,
                "referral_types": ", ".join(getattr(row, "referral_types", [])) if getattr(row, "referral_types", None) else "",  # Comma-separated string
                "referral_ids": ", ".join(getattr(row, "referral_ids", [])) if getattr(row, "referral_ids", None) else "",  # Comma-separated string
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
            # Generate CSV content with UTF-8 encoding (with BOM for Excel compatibility)
            csv_content = df.to_csv(index=False)
            # Add UTF-8 BOM for Excel compatibility
            csv_bytes = "\ufeff".encode("utf-8") + csv_content.encode("utf-8")

            return Response(
                content=csv_bytes,
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
    referral_type: Optional[str] = Query(
        None, description="Filter by Partner Center referral type (co-sell, marketplace, solution-provider)"
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
    - referral_type: Filter by Partner Center referral type (co-sell, marketplace, solution-provider)
    - favorite: Filter by favorites (true = only favorites, false = all leads)
    - sort_by: Sort by field (domain, readiness_score, priority_score, segment, provider, scanned_at)
    - sort_order: Sort order (asc or desc, default: asc)
    - page: Page number (1-based, default: 1)
    - page_size: Number of items per page (default: 50, max: 200)
    - search: Full-text search in domain, canonical_name, and provider

    Returns:
        LeadsListResponse with paginated leads and metadata
    """
    # Build query using leads_ready VIEW with LEFT JOIN to partner_center_referrals
    # Use DISTINCT ON (domain) to prevent duplicates when there are multiple domain_signals or lead_scores
    # View includes G20 columns (tenant_size, local_provider, dmarc_coverage) and CSP P-Model columns
    # LEFT JOIN partner_center_referrals to get referral_type (Task 2.5)
    # Aggregate link_status for multiple referrals: if all same, use it; otherwise 'mixed'
    query = """
        SELECT DISTINCT ON (lr.domain)
            lr.company_id,
            lr.canonical_name,
            lr.domain,
            lr.provider,
            lr.tenant_size,
            lr.local_provider,
            lr.country,
            lr.spf,
            lr.dkim,
            lr.dmarc_policy,
            lr.dmarc_coverage,
            lr.mx_root,
            lr.registrar,
            lr.expires_at,
            lr.nameservers,
            lr.scan_status,
            lr.scanned_at,
            lr.readiness_score,
            lr.segment,
            lr.reason,
            lr.technical_heat,
            lr.commercial_segment,
            lr.commercial_heat,
            lr.priority_category,
            lr.priority_label,
            MAX(pcr.referral_type) AS referral_type,
            -- Calculate aggregated link_status: normalize NULL to 'none' when no referrals, 'unlinked' when referral exists but status is NULL
            -- Also normalize 'auto_linked' to 'linked' for consistency
            CASE 
                WHEN COUNT(pcr.id) = 0 THEN 'none'
                WHEN COUNT(DISTINCT COALESCE(
                    CASE WHEN pcr.link_status = 'auto_linked' THEN 'linked' ELSE pcr.link_status END, 
                    'unlinked'
                )) = 1 
                     THEN MIN(COALESCE(
                         CASE WHEN pcr.link_status = 'auto_linked' THEN 'linked' ELSE pcr.link_status END,
                         'unlinked'
                     ))
                ELSE 'mixed'
            END AS aggregated_link_status,
            -- Get primary referral_id: deterministic ordering (most recent referral first)
            COALESCE(
                (SELECT pcr_inner.referral_id 
                 FROM partner_center_referrals pcr_inner 
                 WHERE pcr_inner.domain = lr.domain 
                 ORDER BY pcr_inner.synced_at DESC, pcr_inner.created_at DESC 
                 LIMIT 1),
                NULL
            ) AS primary_referral_id,
            -- Solution 2: Multiple referrals aggregate (MVP)
            COUNT(pcr.id) AS referral_count,
            ARRAY_AGG(DISTINCT pcr.referral_type) FILTER (WHERE pcr.referral_type IS NOT NULL) AS referral_types,
            ARRAY_AGG(pcr.referral_id ORDER BY pcr.synced_at DESC, pcr.created_at DESC) 
                FILTER (WHERE pcr.referral_id IS NOT NULL) AS referral_ids
        FROM leads_ready lr
        LEFT JOIN partner_center_referrals pcr ON lr.domain = pcr.domain
        WHERE 1=1
    """

    params = {}

    # Add filters
    if segment:
        query += " AND lr.segment = :segment"
        params["segment"] = segment

    if min_score is not None:
        query += " AND lr.readiness_score >= :min_score"
        params["min_score"] = min_score

    if provider:
        query += " AND lr.provider = :provider"
        params["provider"] = provider

    # Partner Center referral type filter
    if referral_type:
        query += " AND pcr.referral_type = :referral_type"
        params["referral_type"] = referral_type

    # G19: Add search filter (full-text search in domain, canonical_name, provider)
    if search:
        search_pattern = f"%{search.lower()}%"
        query += """ AND (
            LOWER(lr.domain) LIKE :search 
            OR LOWER(lr.canonical_name) LIKE :search 
            OR LOWER(lr.provider) LIKE :search
        )"""
        params["search"] = search_pattern

    # Only return leads that have been scanned (have a score)
    query += " AND lr.readiness_score IS NOT NULL"

    # GROUP BY is needed for aggregate functions (aggregated_link_status, primary_referral_id)
    query += " GROUP BY lr.company_id, lr.canonical_name, lr.domain, lr.provider, lr.tenant_size, lr.local_provider, lr.country, lr.spf, lr.dkim, lr.dmarc_policy, lr.dmarc_coverage, lr.mx_root, lr.registrar, lr.expires_at, lr.nameservers, lr.scan_status, lr.scanned_at, lr.readiness_score, lr.segment, lr.reason, lr.technical_heat, lr.commercial_segment, lr.commercial_heat, lr.priority_category, lr.priority_label"
    # Note: DISTINCT ON requires domain to be first in ORDER BY
    # We'll sort by priority_score in Python after calculating it
    # because priority_score is computed from segment + readiness_score
    # Default sorting (if sort_by not specified) is by priority_score
    query += " ORDER BY lr.domain, lr.scanned_at DESC NULLS LAST"

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
            
            # Build infrastructure summary (Level 1 - IP enrichment)
            infrastructure_summary = build_infra_summary(row.domain, db)
            
            # D365 fields (Phase 3)
            d365_sync_status = getattr(row, "d365_sync_status", None)
            # Normalize status: 'pending' -> 'not_synced' for UI consistency
            if d365_sync_status == "pending":
                d365_sync_status = "not_synced"
            elif d365_sync_status is None:
                d365_sync_status = "not_synced"
            
            d365_sync_last_at = None
            if getattr(row, "d365_sync_last_at", None):
                d365_sync_last_at = getattr(row, "d365_sync_last_at").isoformat() if hasattr(getattr(row, "d365_sync_last_at"), "isoformat") else str(getattr(row, "d365_sync_last_at"))
            
            d365_lead_id = getattr(row, "d365_lead_id", None)
            
            # Generate D365 lead URL if base_url and lead_id are available
            d365_lead_url = None
            if d365_lead_id and settings.d365_base_url:
                app_id_param = f"&appid={settings.d365_app_id}" if settings.d365_app_id else ""
                d365_lead_url = f"{settings.d365_base_url}/main.aspx?pagetype=entityrecord&etn=lead&id={d365_lead_id}{app_id_param}"

            lead = LeadResponse(
                company_id=row.company_id,
                canonical_name=row.canonical_name,
                domain=row.domain,
                provider=row.provider,
                tenant_size=row.tenant_size,  # G20: Tenant size (now in view)
                local_provider=row.local_provider,  # G20: Local provider (now in view)
                country=row.country,
                spf=row.spf,
                dkim=row.dkim,
                dmarc_policy=row.dmarc_policy,
                dmarc_coverage=row.dmarc_coverage,  # G20: DMARC coverage (now in view)
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
                # CSP P-Model fields (Phase 2)
                technical_heat=getattr(row, "technical_heat", None),
                commercial_segment=getattr(row, "commercial_segment", None),
                commercial_heat=getattr(row, "commercial_heat", None),
                priority_category=getattr(row, "priority_category", None),
                priority_label=getattr(row, "priority_label", None),
                infrastructure_summary=infrastructure_summary,
                referral_type=getattr(row, "referral_type", None),  # Task 2.5: Partner Center referral type
                link_status=getattr(row, "aggregated_link_status", None) or "none",  # Partner Center link status (linked/unlinked/mixed/none) - normalize NULL to 'none'
                referral_id=getattr(row, "primary_referral_id", None),  # Primary referral ID (if multiple exist)
                # Solution 2: Multiple referrals aggregate (MVP)
                referral_count=getattr(row, "referral_count", 0) or 0,  # Total referral count
                referral_types=list(getattr(row, "referral_types", [])) if getattr(row, "referral_types", None) else [],  # Array of distinct referral types
                referral_ids=list(getattr(row, "referral_ids", [])) if getattr(row, "referral_ids", None) else [],  # Array of referral IDs (priority order)
                # D365 Integration fields (Phase 3)
                d365_sync_status=d365_sync_status,
                d365_sync_last_at=d365_sync_last_at,
                d365_lead_id=d365_lead_id,
                d365_lead_url=d365_lead_url,
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
    # LEFT JOIN partner_center_referrals to get referral_type (Task 2.5)
    # Aggregate link_status for multiple referrals: if all same, use it; otherwise 'mixed'
    query = """
        SELECT 
            c.id AS company_id,
            c.canonical_name,
            c.domain,
            c.provider,
            c.tenant_size,
            c.country,
            c.contact_emails,
            c.contact_quality_score,
            c.linkedin_pattern,
            ds.spf,
            ds.dkim,
            ds.dmarc_policy,
            ds.dmarc_coverage,
            ds.mx_root,
            ds.local_provider,
            ds.registrar,
            ds.expires_at,
            ds.nameservers,
            ds.scan_status,
            ds.scanned_at,
            ls.readiness_score,
            ls.segment,
            ls.reason,
            ls.technical_heat,
            ls.commercial_segment,
            ls.commercial_heat,
            ls.priority_category,
            ls.priority_label,
            c.d365_lead_id,
            c.d365_sync_status,
            c.d365_sync_last_at,
            MAX(pcr.referral_type) AS referral_type,
            -- Calculate aggregated link_status: normalize NULL to 'none' when no referrals, 'unlinked' when referral exists but status is NULL
            -- Also normalize 'auto_linked' to 'linked' for consistency
            CASE 
                WHEN COUNT(pcr.id) = 0 THEN 'none'
                WHEN COUNT(DISTINCT COALESCE(
                    CASE WHEN pcr.link_status = 'auto_linked' THEN 'linked' ELSE pcr.link_status END, 
                    'unlinked'
                )) = 1 
                     THEN MIN(COALESCE(
                         CASE WHEN pcr.link_status = 'auto_linked' THEN 'linked' ELSE pcr.link_status END,
                         'unlinked'
                     ))
                ELSE 'mixed'
            END AS aggregated_link_status,
            -- Get primary referral_id: deterministic ordering (most recent referral first)
            COALESCE(
                (SELECT pcr_inner.referral_id 
                 FROM partner_center_referrals pcr_inner 
                 WHERE pcr_inner.domain = c.domain 
                 ORDER BY pcr_inner.synced_at DESC, pcr_inner.created_at DESC 
                 LIMIT 1),
                NULL
            ) AS primary_referral_id,
            -- Solution 2: Multiple referrals aggregate (MVP)
            COUNT(pcr.id) AS referral_count,
            ARRAY_AGG(DISTINCT pcr.referral_type) FILTER (WHERE pcr.referral_type IS NOT NULL) AS referral_types,
            ARRAY_AGG(pcr.referral_id ORDER BY pcr.synced_at DESC, pcr.created_at DESC) 
                FILTER (WHERE pcr.referral_id IS NOT NULL) AS referral_ids
        FROM companies c
        LEFT JOIN domain_signals ds ON c.domain = ds.domain
        LEFT JOIN lead_scores ls ON c.domain = ls.domain
        LEFT JOIN partner_center_referrals pcr ON c.domain = pcr.domain
        WHERE c.domain = :domain
        GROUP BY c.id, c.canonical_name, c.domain, c.provider, c.tenant_size, c.country, c.contact_emails, c.contact_quality_score, c.linkedin_pattern, ds.spf, ds.dkim, ds.dmarc_policy, ds.dmarc_coverage, ds.mx_root, ds.local_provider, ds.registrar, ds.expires_at, ds.nameservers, ds.scan_status, ds.scanned_at, ls.readiness_score, ls.segment, ls.reason, ls.technical_heat, ls.commercial_segment, ls.commercial_heat, ls.priority_category, ls.priority_label, c.d365_lead_id, c.d365_sync_status, c.d365_sync_last_at
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
        
        # Build infrastructure summary (Level 1 - IP enrichment)
        infrastructure_summary = build_infra_summary(normalized_domain, db)

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
        
        # D365 fields (Phase 3)
        d365_sync_status = getattr(row, "d365_sync_status", None)
        # Normalize status: 'pending' -> 'not_synced' for UI consistency
        if d365_sync_status == "pending":
            d365_sync_status = "not_synced"
        elif d365_sync_status is None:
            d365_sync_status = "not_synced"
        
        d365_sync_last_at = None
        if getattr(row, "d365_sync_last_at", None):
            d365_sync_last_at = getattr(row, "d365_sync_last_at").isoformat() if hasattr(getattr(row, "d365_sync_last_at"), "isoformat") else str(getattr(row, "d365_sync_last_at"))
        
        d365_lead_id = getattr(row, "d365_lead_id", None)
        
        # Generate D365 lead URL if base_url and lead_id are available
        d365_lead_url = None
        if d365_lead_id and settings.d365_base_url:
            app_id_param = f"&appid={settings.d365_app_id}" if settings.d365_app_id else ""
            d365_lead_url = f"{settings.d365_base_url}/main.aspx?pagetype=entityrecord&etn=lead&id={d365_lead_id}{app_id_param}"

        return LeadResponse(
            company_id=row.company_id,
            canonical_name=row.canonical_name,
            domain=row.domain,
            provider=row.provider,
            tenant_size=getattr(row, "tenant_size", None),  # G20: Tenant size
            local_provider=getattr(row, "local_provider", None),  # G20: Local provider
            country=row.country,
            contact_emails=contact_emails,
            contact_quality_score=row.contact_quality_score,
            linkedin_pattern=row.linkedin_pattern,
            spf=row.spf,
            dkim=row.dkim,
            dmarc_policy=row.dmarc_policy,
            dmarc_coverage=getattr(row, "dmarc_coverage", None),  # G20: DMARC coverage
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
            # CSP P-Model fields (Phase 2)
            technical_heat=getattr(row, "technical_heat", None),
            commercial_segment=getattr(row, "commercial_segment", None),
            commercial_heat=getattr(row, "commercial_heat", None),
            priority_category=getattr(row, "priority_category", None),
            priority_label=getattr(row, "priority_label", None),
            infrastructure_summary=infrastructure_summary,
            referral_type=getattr(row, "referral_type", None),  # Task 2.5: Partner Center referral type
            link_status=getattr(row, "aggregated_link_status", None) or "none",  # Partner Center link status (linked/unlinked/mixed/none) - normalize NULL to 'none'
            referral_id=getattr(row, "primary_referral_id", None),  # Primary referral ID (if multiple exist)
            # Solution 2: Multiple referrals aggregate (MVP)
            referral_count=getattr(row, "referral_count", 0) or 0,  # Total referral count
            referral_types=list(getattr(row, "referral_types", [])) if getattr(row, "referral_types", None) else [],  # Array of distinct referral types
            referral_ids=list(getattr(row, "referral_ids", [])) if getattr(row, "referral_ids", None) else [],  # Array of referral IDs (priority order)
            # D365 Integration fields (Phase 3)
            d365_sync_status=d365_sync_status,
            d365_sync_last_at=d365_sync_last_at,
            d365_lead_id=d365_lead_id,
            d365_lead_url=d365_lead_url,
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


class IpEnrichmentSchema(BaseModel):
    """IP enrichment schema for score breakdown."""

    country: Optional[str] = None
    city: Optional[str] = None
    isp: Optional[str] = None
    is_proxy: Optional[bool] = None
    proxy_type: Optional[str] = None


class ScoreBreakdownResponse(BaseModel):
    """Response model for score breakdown (G19 + G20 + IP Enrichment + Phase 3 P-Model)."""

    base_score: int
    provider: Dict[str, Any]  # {"name": str, "points": int}
    signal_points: Dict[str, int]  # {"spf": int, "dkim": int, "dmarc_*": int}
    risk_points: Dict[str, int]  # {"no_spf": int, "no_dkim": int, ...}
    total_score: int
    # G20: Domain Intelligence fields
    tenant_size: Optional[str] = None  # G20: Tenant size (small/medium/large)
    local_provider: Optional[str] = None  # G20: Local provider name (e.g., TürkHost)
    dmarc_coverage: Optional[int] = None  # G20: DMARC coverage (0-100)
    dmarc_policy: Optional[str] = None  # v1.1: DMARC policy (none/quarantine/reject) - for UI logic
    # IP Enrichment (Minimal UI)
    ip_enrichment: Optional[IpEnrichmentSchema] = None
    # Phase 3: CSP P-Model fields
    technical_heat: Optional[str] = None  # 'Hot', 'Warm', 'Cold'
    commercial_segment: Optional[str] = None  # 'GREENFIELD', 'COMPETITIVE', 'WEAK_PARTNER', 'RENEWAL', 'LOW_INTENT', 'NO_GO'
    commercial_heat: Optional[str] = None  # 'HIGH', 'MEDIUM', 'LOW'
    priority_category: Optional[str] = None  # 'P1', 'P2', 'P3', 'P4', 'P5', 'P6'
    priority_label: Optional[str] = None  # Human-readable label (e.g., 'High Potential Greenfield')
    # Solution 2: Partner Center referral aggregate info (for breakdown modal)
    referral_type: Optional[str] = None  # Primary referral type
    link_status: Optional[str] = None  # Primary referral link status
    referral_id: Optional[str] = None  # Primary referral ID
    referral_count: int = 0  # Total referral count
    referral_types: List[str] = []  # Array of distinct referral types
    referral_ids: List[str] = []  # Array of referral IDs (priority order)


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
        raise HTTPException(status_code=400, detail="Geçersiz domain formatı")

    # Get domain data
    company = db.query(Company).filter(Company.domain == normalized_domain).first()
    if not company:
        raise HTTPException(
            status_code=404,
            detail=f"Domain {normalized_domain} bulunamadı. Lütfen önce /ingest/domain ile domain'i ekleyin",
        )

    # Get domain signals
    domain_signal = (
        db.query(DomainSignal).filter(DomainSignal.domain == normalized_domain).first()
    )

    if not domain_signal or domain_signal.scan_status != "completed":
        raise HTTPException(
            status_code=404,
            detail=f"Domain {normalized_domain} henüz taranmamış. Lütfen önce /scan/domain ile tarayın.",
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

    # G20: Add domain intelligence fields
    breakdown_dict = breakdown.to_dict()
    breakdown_dict["tenant_size"] = company.tenant_size  # G20: Tenant size
    breakdown_dict["local_provider"] = domain_signal.local_provider  # G20: Local provider
    breakdown_dict["dmarc_coverage"] = domain_signal.dmarc_coverage  # G20: DMARC coverage
    breakdown_dict["dmarc_policy"] = domain_signal.dmarc_policy  # v1.1: DMARC policy (for UI logic - show policy vs coverage)

    # IP Enrichment (Minimal UI)
    from app.core.enrichment_service import latest_ip_enrichment

    ip_enrichment_record = latest_ip_enrichment(normalized_domain, db)
    if ip_enrichment_record:
        breakdown_dict["ip_enrichment"] = {
            "country": ip_enrichment_record.country,
            "city": ip_enrichment_record.city,
            "isp": ip_enrichment_record.isp,
            "is_proxy": ip_enrichment_record.is_proxy,
            "proxy_type": ip_enrichment_record.proxy_type,
        }
    else:
        breakdown_dict["ip_enrichment"] = None

    # Phase 3: Add CSP P-Model fields from lead_scores
    lead_score = (
        db.query(LeadScore)
        .filter(LeadScore.domain == normalized_domain)
        .first()
    )
    if lead_score:
        breakdown_dict["technical_heat"] = lead_score.technical_heat
        breakdown_dict["commercial_segment"] = lead_score.commercial_segment
        breakdown_dict["commercial_heat"] = lead_score.commercial_heat
        breakdown_dict["priority_category"] = lead_score.priority_category
        breakdown_dict["priority_label"] = lead_score.priority_label
    
    # Partner Center referral info (for breakdown modal) - Solution 2: Aggregate info
    from app.db.models import PartnerCenterReferral
    referrals = (
        db.query(PartnerCenterReferral)
        .filter(PartnerCenterReferral.domain == normalized_domain)
        .order_by(PartnerCenterReferral.synced_at.desc(), PartnerCenterReferral.created_at.desc())
        .all()
    )
    if referrals:
        # Primary referral (most recent)
        primary_referral = referrals[0]
        breakdown_dict["referral_type"] = primary_referral.referral_type
        breakdown_dict["link_status"] = primary_referral.link_status
        breakdown_dict["referral_id"] = primary_referral.referral_id
        # Solution 2: Aggregate info
        breakdown_dict["referral_count"] = len(referrals)
        breakdown_dict["referral_types"] = list(set([r.referral_type for r in referrals if r.referral_type]))
        breakdown_dict["referral_ids"] = [r.referral_id for r in referrals if r.referral_id]
    else:
        breakdown_dict["referral_type"] = None
        breakdown_dict["link_status"] = None
        breakdown_dict["referral_id"] = None
        # Solution 2: Aggregate info (empty)
        breakdown_dict["referral_count"] = 0
        breakdown_dict["referral_types"] = []
        breakdown_dict["referral_ids"] = []
    
    if not lead_score:
        # Fallback: Calculate P-model fields on the fly if not in DB
        from app.core.scorer import score_domain
        scoring_result = score_domain(
            domain=normalized_domain,
            provider=company.provider or "Unknown",
            signals=signals,
            mx_records=mx_records,
            use_cache=False,  # Don't cache here, just calculate
        )
        breakdown_dict["technical_heat"] = scoring_result.get("technical_heat")
        breakdown_dict["commercial_segment"] = scoring_result.get("commercial_segment")
        breakdown_dict["commercial_heat"] = scoring_result.get("commercial_heat")
        breakdown_dict["priority_category"] = scoring_result.get("priority_category")
        breakdown_dict["priority_label"] = scoring_result.get("priority_label")

    return ScoreBreakdownResponse(**breakdown_dict)
