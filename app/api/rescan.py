"""ReScan endpoints for domain re-scanning with change detection (G18)."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.db.session import get_db
from app.db.models import Company
from app.core.normalizer import normalize_domain
from app.core.rescan import rescan_domain
from app.core.progress_tracker import get_progress_tracker
from app.core.tasks import bulk_scan_task
from app.core.constants import MAX_BULK_SCAN_DOMAINS
import uuid


router = APIRouter(prefix="/scan", tags=["rescan"])


class RescanDomainResponse(BaseModel):
    """Response model for domain rescan."""
    domain: str
    success: bool
    changes_detected: bool
    signal_changes: int
    score_changes: int
    alerts_created: int
    changes: List[dict]
    result: Optional[dict] = None
    error: Optional[str] = None


@router.post("/{domain}/rescan", response_model=RescanDomainResponse)
async def rescan_single_domain(
    domain: str,
    db: Session = Depends(get_db)
):
    """
    Re-scan a single domain and detect changes.
    
    This endpoint:
    - Re-scans the domain (DNS + WHOIS)
    - Detects changes in signals (SPF, DKIM, DMARC, MX)
    - Detects changes in scores and segments
    - Creates alerts for detected changes
    - Updates auto-tags if applicable
    
    Args:
        domain: Domain name (will be normalized)
        db: Database session
        
    Returns:
        RescanDomainResponse with scan result and detected changes
        
    Raises:
        404: If domain not found
        400: If domain is invalid
    """
    # Normalize domain
    normalized_domain = normalize_domain(domain)
    
    if not normalized_domain:
        raise HTTPException(status_code=400, detail="Invalid domain format")
    
    # Check if domain exists
    company = db.query(Company).filter(Company.domain == normalized_domain).first()
    if not company:
        raise HTTPException(
            status_code=404,
            detail=f"Domain {normalized_domain} not found. Please ingest the domain first using /ingest/domain"
        )
    
    try:
        # Perform rescan
        result = rescan_domain(normalized_domain, db)
        
        if not result.get("success"):
            return RescanDomainResponse(
                domain=normalized_domain,
                success=False,
                changes_detected=False,
                signal_changes=0,
                score_changes=0,
                alerts_created=0,
                changes=[],
                error=result.get("error", "Unknown error")
            )
        
        return RescanDomainResponse(
            domain=normalized_domain,
            success=True,
            changes_detected=result.get("changes_detected", False),
            signal_changes=result.get("signal_changes", 0),
            score_changes=result.get("score_changes", 0),
            alerts_created=result.get("alerts_created", 0),
            changes=result.get("changes", []),
            result=result.get("result")
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/bulk/rescan")
async def bulk_rescan(
    domain_list: Optional[str] = Query(None, description="Comma-separated list of domains"),
    db: Session = Depends(get_db)
):
    """
    Create a bulk rescan job for multiple domains.
    
    This endpoint creates an async job that will:
    - Re-scan all specified domains
    - Detect changes in signals and scores
    - Create alerts for detected changes
    
    Args:
        domain_list: Comma-separated list of domains (e.g., "example.com,test.com")
        db: Database session
        
    Returns:
        Job ID and status
        
    Raises:
        400: If no domains provided or invalid format
    """
    if not domain_list:
        raise HTTPException(status_code=400, detail="domain_list parameter is required")
    
    # Parse domain list
    domains = [d.strip() for d in domain_list.split(",") if d.strip()]
    
    if not domains:
        raise HTTPException(status_code=400, detail="No valid domains provided")
    
    if len(domains) > MAX_BULK_SCAN_DOMAINS:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_BULK_SCAN_DOMAINS} domains per bulk rescan")
    
    # Normalize domains
    normalized_domains = []
    for domain in domains:
        normalized = normalize_domain(domain)
        if normalized:
            normalized_domains.append(normalized)
    
    if not normalized_domains:
        raise HTTPException(status_code=400, detail="No valid domains after normalization")
    
    # Initialize progress tracker and create job (creates job_id automatically)
    tracker = get_progress_tracker()
    job_id = tracker.create_job(normalized_domains)
    
    # Start async rescan task (with is_rescan=True for change detection)
    bulk_scan_task.delay(job_id, is_rescan=True)
    
    return {
        "job_id": job_id,
        "status": "pending",
        "total": len(normalized_domains),
        "message": "Bulk rescan job created"
    }

