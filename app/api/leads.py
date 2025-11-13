"""Leads endpoints for querying analyzed domains."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List
from pydantic import BaseModel
from app.db.session import get_db
from app.core.normalizer import normalize_domain
from app.core.priority import calculate_priority_score


router = APIRouter(prefix="/leads", tags=["leads"])


class LeadResponse(BaseModel):
    """Response model for a single lead."""
    company_id: Optional[int] = None
    canonical_name: Optional[str] = None
    domain: str
    provider: Optional[str] = None
    country: Optional[str] = None
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


@router.get("", response_model=List[LeadResponse])
async def get_leads(
    segment: Optional[str] = Query(None, description="Filter by segment (Migration, Existing, Cold, Skip)"),
    min_score: Optional[int] = Query(None, ge=0, le=100, description="Minimum readiness score (0-100)"),
    provider: Optional[str] = Query(None, description="Filter by provider (M365, Google, etc.)"),
    db: Session = Depends(get_db)
):
    """
    Get filtered list of leads.
    
    Query parameters:
    - segment: Filter by segment (Migration, Existing, Cold, Skip)
    - min_score: Minimum readiness score (0-100)
    - provider: Filter by provider name
    
    Returns:
        List of LeadResponse objects matching the filters
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
    
    # Only return leads that have been scanned (have a score)
    query += " AND readiness_score IS NOT NULL"
    
    # Order by score descending
    query += " ORDER BY readiness_score DESC, domain ASC"
    
    try:
        result = db.execute(text(query), params)
        rows = result.fetchall()
        
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
                priority_score=priority_score
            )
            leads.append(lead)
        
        return leads
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{domain}", response_model=LeadResponse)
async def get_lead(
    domain: str,
    db: Session = Depends(get_db)
):
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
                detail=f"Domain {normalized_domain} not found. Please ingest the domain first using /ingest/domain"
            )
        
        # Check if domain has been scanned
        if row.readiness_score is None:
            raise HTTPException(
                status_code=404,
                detail=f"Domain {normalized_domain} has not been scanned yet. Please use /scan/domain first."
            )
        
        # Calculate priority score
        priority_score = calculate_priority_score(row.segment, row.readiness_score)
        
        return LeadResponse(
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
            priority_score=priority_score
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

