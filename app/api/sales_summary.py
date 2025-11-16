"""Sales summary endpoint for sales intelligence."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from app.db.session import get_db
from app.core.normalizer import normalize_domain
from app.core.sales_engine import generate_sales_summary
from app.db.models import Company, DomainSignal, LeadScore, User
from app.core.logging import logger
from app.config import settings
from pydantic import BaseModel

router = APIRouter(prefix="/leads", tags=["sales", "legacy"])


class SalesSummaryResponse(BaseModel):
    """Response model for sales summary."""

    domain: str
    one_liner: str
    call_script: list[str]
    discovery_questions: list[str]
    offer_tier: dict
    opportunity_potential: int
    urgency: str
    metadata: dict


@router.get("/{domain}/sales-summary", response_model=SalesSummaryResponse)
async def get_sales_summary(
    domain: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Get complete sales intelligence summary for a lead.

    Args:
        domain: Domain name (will be normalized)
        request: FastAPI request object (for user tracking)
        db: Database session

    Returns:
        SalesSummaryResponse with complete sales intelligence

    Raises:
        404: If domain not found or not scanned
    """
    # Normalize domain
    normalized_domain = normalize_domain(domain)

    if not normalized_domain:
        raise HTTPException(status_code=400, detail="Invalid domain format")

    # Query company and related data
    company = db.query(Company).filter(Company.domain == normalized_domain).first()

    if not company:
        raise HTTPException(
            status_code=404, detail=f"Domain not found: {normalized_domain}"
        )

    # Query domain signals
    domain_signal = (
        db.query(DomainSignal).filter(DomainSignal.domain == normalized_domain).first()
    )

    # Query lead score
    lead_score = (
        db.query(LeadScore).filter(LeadScore.domain == normalized_domain).first()
    )

    # Extract data
    provider = company.provider
    segment = lead_score.segment if lead_score else None
    readiness_score = lead_score.readiness_score if lead_score else None
    priority_score = None  # Will be calculated if needed
    tenant_size = company.tenant_size
    local_provider = domain_signal.local_provider if domain_signal else None
    spf = domain_signal.spf if domain_signal else None
    dkim = domain_signal.dkim if domain_signal else None
    dmarc_policy = domain_signal.dmarc_policy if domain_signal else None
    dmarc_coverage = domain_signal.dmarc_coverage if domain_signal else None
    contact_quality_score = company.contact_quality_score
    expires_at = domain_signal.expires_at if domain_signal else None

    # Calculate priority score if needed (import from priority module)
    if segment and readiness_score is not None:
        from app.core.priority import calculate_priority_score

        priority_score = calculate_priority_score(segment, readiness_score)

    # Get tuning factor from config
    tuning_factor = settings.sales_engine_opportunity_factor

    # Generate sales summary
    summary = generate_sales_summary(
        domain=normalized_domain,
        provider=provider,
        segment=segment,
        readiness_score=readiness_score,
        priority_score=priority_score,
        tenant_size=tenant_size,
        local_provider=local_provider,
        spf=spf,
        dkim=dkim,
        dmarc_policy=dmarc_policy,
        dmarc_coverage=dmarc_coverage,
        contact_quality_score=contact_quality_score,
        expires_at=expires_at,
        tuning_factor=tuning_factor,
    )

    # Get user identifier (try auth first, fallback to session)
    user_id = None
    user_email = None
    
    try:
        # Try to get authenticated user from Authorization header
        from fastapi.security import HTTPBearer
        from app.api.auth import get_current_user
        
        security = HTTPBearer(auto_error=False)
        auth_header = request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            from app.core.auth import jwt_manager
            
            payload = jwt_manager.verify_token(token, token_type="access")
            if payload:
                user_id_from_token = int(payload.get("sub"))
                user = db.query(User).filter(User.id == user_id_from_token).first()
                if user:
                    user_id = user.id
                    user_email = user.email
    except Exception:
        pass
    
    # Fallback: try session-based user ID
    if not user_id:
        try:
            session_id = request.cookies.get("session_id")
            if session_id:
                user_id = f"session:{session_id}"
        except Exception:
            pass

    # Log sales summary view event
    logger.info(
        "sales_summary_viewed",
        domain=normalized_domain,
        user_id=user_id,
        user_email=user_email,
        segment=segment,
        offer_tier=summary["offer_tier"]["tier"],
        opportunity_potential=summary["opportunity_potential"],
        urgency=summary["urgency"],
        tenant_size=tenant_size,
        provider=provider,
    )

    return SalesSummaryResponse(**summary)

