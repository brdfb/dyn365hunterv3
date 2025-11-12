"""Scan endpoints for domain analysis and scoring."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from app.db.session import get_db
from app.db.models import Company, DomainSignal, LeadScore
from app.core.normalizer import normalize_domain
from app.core.analyzer_dns import analyze_dns
from app.core.analyzer_whois import get_whois_info
from app.core.provider_map import classify_provider
from app.core.scorer import score_domain


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
        
        # Update company provider if we have new information
        if provider and provider != "Unknown":
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
        
        # Upsert domain_signals
        domain_signal = db.query(DomainSignal).filter(DomainSignal.domain == domain).first()
        
        if domain_signal:
            # Update existing signal
            domain_signal.spf = dns_result.get("spf", False)
            domain_signal.dkim = dns_result.get("dkim", False)
            domain_signal.dmarc_policy = dns_result.get("dmarc_policy")
            domain_signal.mx_root = mx_root
            domain_signal.scan_status = scan_status
            
            # Update WHOIS data if available
            if whois_result:
                domain_signal.registrar = whois_result.get("registrar")
                domain_signal.expires_at = whois_result.get("expires_at")
                domain_signal.nameservers = whois_result.get("nameservers")
        else:
            # Create new signal
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
        
        # Upsert lead_scores
        lead_score = db.query(LeadScore).filter(LeadScore.domain == domain).first()
        
        if lead_score:
            # Update existing score
            lead_score.readiness_score = scoring_result["score"]
            lead_score.segment = scoring_result["segment"]
            lead_score.reason = scoring_result["reason"]
        else:
            # Create new score
            lead_score = LeadScore(
                domain=domain,
                readiness_score=scoring_result["score"],
                segment=scoring_result["segment"],
                reason=scoring_result["reason"]
            )
            db.add(lead_score)
        
        # Commit all changes
        db.commit()
        db.refresh(domain_signal)
        db.refresh(lead_score)
        
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
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

