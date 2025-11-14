"""Leads endpoints for querying analyzed domains."""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
import pandas as pd
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


@router.get("/export")
async def export_leads(
    segment: Optional[str] = Query(None, description="Filter by segment (Migration, Existing, Cold, Skip)"),
    min_score: Optional[int] = Query(None, ge=0, le=100, description="Minimum readiness score (0-100)"),
    provider: Optional[str] = Query(None, description="Filter by provider (M365, Google, etc.)"),
    format: str = Query("csv", pattern="^(csv|xlsx)$", description="Export format (csv or xlsx)"),
    db: Session = Depends(get_db)
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
                "reason": row.reason or ""
            }
            leads_data.append(lead_dict)
        
        # Sort by priority_score ASC (1 = highest priority), then readiness_score DESC
        leads_data.sort(key=lambda x: (
            x.get("priority_score", 999),
            -x.get("readiness_score", 0)
        ))
        
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
                    "Content-Type": "text/csv; charset=utf-8"
                }
            )
        else:  # xlsx
            # Generate Excel content
            from io import BytesIO
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Leads')
            
            output.seek(0)
            excel_content = output.read()
            
            return Response(
                content=excel_content,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": f"attachment; filename=leads_{timestamp}.xlsx"
                }
            )
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Export error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while exporting leads: {str(e)}"
        )


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
    
    # Note: We'll sort by priority_score in Python after calculating it
    # because priority_score is computed from segment + readiness_score
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
        
        # Sort by priority_score ASC (1 = highest priority), then readiness_score DESC
        # This ensures Migration leads with high scores appear first
        leads.sort(key=lambda x: (
            x.priority_score if x.priority_score is not None else 999,
            -(x.readiness_score if x.readiness_score is not None else 0)
        ))
        
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

