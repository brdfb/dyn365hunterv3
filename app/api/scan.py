"""Scan endpoints for domain analysis and scoring."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from app.db.session import get_db
from app.db.models import Company, DomainSignal, LeadScore, ProviderChangeHistory
from app.core.normalizer import normalize_domain
from app.core.analyzer_dns import analyze_dns
from app.core.analyzer_whois import get_whois_info
from app.core.provider_map import classify_provider
from app.core.scorer import score_domain
from app.core.progress_tracker import get_progress_tracker
from app.core.tasks import bulk_scan_task
from app.core.auto_tagging import apply_auto_tags


router = APIRouter(prefix="/scan", tags=["scan"])


class ScanDomainRequest(BaseModel):
    """Request model for domain scanning."""
    domain: str = Field(..., description="Domain name to scan")
    
    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        """Validate and normalize domain."""
        normalized = normalize_domain(v)
        if not normalized:
            raise ValueError("Invalid domain format")
        return normalized


class ScanDomainResponse(BaseModel):
    """Response model for domain scanning."""
    domain: str
    score: int
    segment: str
    reason: str
    provider: Optional[str] = None
    mx_root: Optional[str] = None
    spf: bool = False
    dkim: bool = False
    dmarc_policy: Optional[str] = None
    scan_status: str


@router.post("/domain", response_model=ScanDomainResponse)
async def scan_domain(
    request: ScanDomainRequest,
    db: Session = Depends(get_db)
):
    """
    Scan a domain for DNS/WHOIS analysis and calculate readiness score.
    
    Performs:
    - DNS analysis (MX, SPF, DKIM, DMARC)
    - WHOIS lookup (optional, graceful fail)
    - Provider classification
    - Scoring and segment determination
    - Saves results to domain_signals and lead_scores tables
    
    Args:
        request: Domain scan request
        db: Database session
        
    Returns:
        ScanDomainResponse with analysis results and score
    """
    domain = request.domain
    
    # Check if company exists
    company = db.query(Company).filter(Company.domain == domain).first()
    if not company:
        raise HTTPException(
            status_code=404,
            detail=f"Domain {domain} not found. Please ingest the domain first using /ingest/domain"
        )
    
    try:
        # Perform DNS analysis
        dns_result = analyze_dns(domain)
        
        # Perform WHOIS lookup (optional, graceful fail)
        whois_result = get_whois_info(domain)
        
        # Determine scan status
        scan_status = dns_result.get("status", "success")
        if scan_status == "success" and whois_result is None:
            # WHOIS failed but DNS succeeded
            scan_status = "whois_failed"
        elif scan_status != "success":
            # DNS failed
            pass  # Keep DNS status
        
        # Classify provider based on MX root
        mx_root = dns_result.get("mx_root")
        provider = classify_provider(mx_root)
        
        # Track provider changes
        previous_provider = company.provider
        provider_changed = False
        
        # Update company provider if we have new information
        if provider and provider != "Unknown":
            if previous_provider != provider:
                provider_changed = True
            company.provider = provider
            db.commit()
        
        # Prepare signals for scoring
        signals = {
            "spf": dns_result.get("spf", False),
            "dkim": dns_result.get("dkim", False),
            "dmarc_policy": dns_result.get("dmarc_policy")
        }
        
        # Calculate score and determine segment
        scoring_result = score_domain(
            domain=domain,
            provider=provider,
            signals=signals,
            mx_records=dns_result.get("mx_records", [])
        )
        
        # Delete any existing domain_signals for this domain (prevent duplicates)
        db.query(DomainSignal).filter(DomainSignal.domain == domain).delete()
        
        # Create new domain_signal
        domain_signal = DomainSignal(
            domain=domain,
            spf=dns_result.get("spf", False),
            dkim=dns_result.get("dkim", False),
            dmarc_policy=dns_result.get("dmarc_policy"),
            mx_root=mx_root,
            registrar=whois_result.get("registrar") if whois_result else None,
            expires_at=whois_result.get("expires_at") if whois_result else None,
            nameservers=whois_result.get("nameservers") if whois_result else None,
            scan_status=scan_status
        )
        db.add(domain_signal)
        
        # Delete any existing lead_scores for this domain (prevent duplicates)
        db.query(LeadScore).filter(LeadScore.domain == domain).delete()
        
        # Create new lead_score
        lead_score = LeadScore(
            domain=domain,
            readiness_score=scoring_result["score"],
            segment=scoring_result["segment"],
            reason=scoring_result["reason"]
        )
        db.add(lead_score)
        
        # Log provider change if detected
        if provider_changed and previous_provider:
            change_history = ProviderChangeHistory(
                domain=domain,
                previous_provider=previous_provider,
                new_provider=provider
            )
            db.add(change_history)
        
        # Commit all changes
        db.commit()
        db.refresh(domain_signal)
        db.refresh(lead_score)
        
        # Apply auto-tagging (G17)
        try:
            apply_auto_tags(domain, db)
            db.commit()
        except Exception as e:
            # Log error but don't fail the scan
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Auto-tagging failed for {domain}: {str(e)}")
        
        # Return response
        return ScanDomainResponse(
            domain=domain,
            score=scoring_result["score"],
            segment=scoring_result["segment"],
            reason=scoring_result["reason"],
            provider=provider,
            mx_root=mx_root,
            spf=dns_result.get("spf", False),
            dkim=dns_result.get("dkim", False),
            dmarc_policy=dns_result.get("dmarc_policy"),
            scan_status=scan_status
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        # Validation errors (e.g., invalid domain format)
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An error occurred while scanning the domain. Please try again later."
        )


class BulkScanRequest(BaseModel):
    """Request model for bulk domain scanning."""
    domain_list: List[str] = Field(..., description="List of domain names to scan", min_length=1, max_length=1000)
    
    @field_validator("domain_list")
    @classmethod
    def validate_domain_list(cls, v: List[str]) -> List[str]:
        """Validate and normalize domain list."""
        normalized = []
        for domain in v:
            normalized_domain = normalize_domain(domain)
            if normalized_domain:
                normalized.append(normalized_domain)
        if not normalized:
            raise ValueError("No valid domains in domain_list")
        return normalized


class BulkScanResponse(BaseModel):
    """Response model for bulk scan job creation."""
    job_id: str
    message: str
    total: int


class BulkScanStatusResponse(BaseModel):
    """Response model for bulk scan job status."""
    job_id: str
    status: str  # pending, running, completed, failed
    progress: int  # 0-100
    total: int
    processed: int
    succeeded: int
    failed: int
    errors: List[dict]


@router.post("/bulk", response_model=BulkScanResponse)
async def scan_bulk(
    request: BulkScanRequest,
    db: Session = Depends(get_db)
):
    """
    Create a bulk scan job for multiple domains.
    
    This endpoint creates an async job that will scan all domains in the background.
    Use GET /scan/bulk/{job_id} to check progress.
    
    Args:
        request: Bulk scan request with domain list
        db: Database session
        
    Returns:
        BulkScanResponse with job_id
    """
    # Validate that all domains exist in database
    missing_domains = []
    for domain in request.domain_list:
        company = db.query(Company).filter(Company.domain == domain).first()
        if not company:
            missing_domains.append(domain)
    
    if missing_domains:
        raise HTTPException(
            status_code=400,
            detail=f"Domains not found. Please ingest first: {', '.join(missing_domains[:5])}"
            + (f" and {len(missing_domains) - 5} more" if len(missing_domains) > 5 else "")
        )
    
    # Create job in progress tracker
    tracker = get_progress_tracker()
    job_id = tracker.create_job(request.domain_list)
    
    # Start bulk scan task
    bulk_scan_task.delay(job_id)
    
    return BulkScanResponse(
        job_id=job_id,
        message="Bulk scan job created successfully",
        total=len(request.domain_list)
    )


@router.get("/bulk/{job_id}", response_model=BulkScanStatusResponse)
async def get_bulk_scan_status(job_id: str):
    """
    Get bulk scan job status and progress.
    
    Args:
        job_id: Job ID from POST /scan/bulk
        
    Returns:
        BulkScanStatusResponse with job status and progress
    """
    tracker = get_progress_tracker()
    job = tracker.get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    # Check if job is completed (all domains processed)
    if job["status"] == "running" and job["processed"] >= job["total"]:
        job["status"] = "completed"
        tracker.set_status(job_id, "completed")
    
    return BulkScanStatusResponse(
        job_id=job_id,
        status=job["status"],
        progress=job.get("progress", 0),
        total=job["total"],
        processed=job["processed"],
        succeeded=job["succeeded"],
        failed=job["failed"],
        errors=job["errors"]
    )


@router.get("/bulk/{job_id}/results")
async def get_bulk_scan_results(job_id: str):
    """
    Get bulk scan job results (only for completed jobs).
    
    Args:
        job_id: Job ID from POST /scan/bulk
        
    Returns:
        List of scan results
    """
    tracker = get_progress_tracker()
    job = tracker.get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job {job_id} is not completed yet. Status: {job['status']}"
        )
    
    results = tracker.get_results(job_id)
    
    return {
        "job_id": job_id,
        "total": job["total"],
        "succeeded": job["succeeded"],
        "failed": job["failed"],
        "results": results
    }

