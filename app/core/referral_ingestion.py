"""Partner Center referral ingestion module."""

import structlog
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.models import RawLead, Company, PartnerCenterReferral, DomainSignal
from app.core.partner_center import PartnerCenterClient
from app.core.normalizer import (
    normalize_domain,
    extract_domain_from_email,
    extract_domain_from_website,
)
from app.core.merger import upsert_companies
from app.core.tasks import scan_single_domain
from app.config import settings
from app.core.logging import logger, mask_pii

logger = structlog.get_logger(__name__)


def detect_referral_type(referral: Dict[str, Any]) -> Optional[str]:
    """
    Detect referral type from Partner Center referral data.
    
    Args:
        referral: Partner Center referral dictionary
        
    Returns:
        Referral type: 'co-sell', 'marketplace', 'solution-provider', or None
    """
    # Partner Center referral types (based on API structure)
    referral_type = referral.get("type") or referral.get("referralType")
    
    if not referral_type:
        return None
    
    referral_type_lower = referral_type.lower()
    
    # Map Partner Center types to our internal types
    if "co-sell" in referral_type_lower or "cosell" in referral_type_lower:
        return "co-sell"
    elif "marketplace" in referral_type_lower:
        return "marketplace"
    elif "solution" in referral_type_lower or "provider" in referral_type_lower:
        return "solution-provider"
    
    return None


def extract_domain_from_referral(referral: Dict[str, Any]) -> Optional[str]:
    """
    Extract domain from referral using fallback chain.
    
    Fallback chain:
    1. Try website: referral.website → extract_domain_from_website() → normalize_domain()
    2. Try email: referral.contact.email → extract_domain_from_email() → normalize_domain()
    3. Skip: Domain yoksa → None (log warning)
    
    Args:
        referral: Partner Center referral dictionary
        
    Returns:
        Normalized domain string, or None if not found
    """
    # 1. Try website
    website = referral.get("website") or referral.get("companyWebsite")
    if website:
        domain = extract_domain_from_website(website)
        if domain:
            logger.debug("partner_center_domain_extracted", source="website", domain=mask_pii(domain))
            return domain
    
    # 2. Try email
    contact = referral.get("contact") or {}
    email = contact.get("email") or referral.get("email")
    if email:
        domain = extract_domain_from_email(email)
        if domain:
            logger.debug("partner_center_domain_extracted", source="email", domain=mask_pii(domain))
            return domain
    
    # 3. Skip (domain not found)
    logger.warning("partner_center_domain_not_found", referral_id=referral.get("id"))
    return None


def apply_azure_tenant_signal(
    db: Session, company: Company, azure_tenant_id: Optional[str]
) -> Company:
    """
    Apply Azure Tenant ID signal to company (provider override).
    
    If azureTenantId exists, override Company.provider='M365'.
    This is done during ingestion only (segment override is in scoring pipeline).
    
    Args:
        db: Database session
        company: Company instance
        azure_tenant_id: Azure Tenant ID from referral
        
    Returns:
        Updated company instance
    """
    if azure_tenant_id:
        company.provider = "M365"
        db.commit()
        db.refresh(company)
        logger.debug(
            "partner_center_azure_tenant_applied",
            domain=mask_pii(company.domain),
            azure_tenant_id=mask_pii(azure_tenant_id),
        )
    
    return company


def ingest_to_raw_leads(
    db: Session, referral: Dict[str, Any], normalized_domain: str
) -> RawLead:
    """
    Ingest referral to raw_leads table (mevcut pattern).
    
    Args:
        db: Database session
        referral: Partner Center referral dictionary
        normalized_domain: Normalized domain string
        
    Returns:
        Created RawLead instance
    """
    contact = referral.get("contact") or {}
    company_name = referral.get("companyName") or referral.get("company_name")
    website = referral.get("website") or referral.get("companyWebsite")
    email = contact.get("email") or referral.get("email")
    
    raw_lead = RawLead(
        source="partnercenter",
        company_name=company_name,
        email=email,
        website=website,
        domain=normalized_domain,
        payload=referral,  # Full referral JSON (JSONB)
    )
    
    db.add(raw_lead)
    db.commit()
    db.refresh(raw_lead)
    
    logger.debug(
        "partner_center_raw_lead_created",
        raw_lead_id=raw_lead.id,
        domain=mask_pii(normalized_domain),
    )
    
    return raw_lead


def upsert_referral_tracking(
    db: Session, referral: Dict[str, Any], normalized_domain: str
) -> PartnerCenterReferral:
    """
    Upsert referral tracking in partner_center_referrals table.
    
    Args:
        db: Database session
        referral: Partner Center referral dictionary
        normalized_domain: Normalized domain string
        
    Returns:
        Created or updated PartnerCenterReferral instance
    """
    referral_id = referral.get("id") or referral.get("referralId")
    if not referral_id:
        raise ValueError("Referral ID not found in referral data")
    
    referral_type = detect_referral_type(referral)
    company_name = referral.get("companyName") or referral.get("company_name")
    azure_tenant_id = referral.get("azureTenantId") or referral.get("azure_tenant_id")
    status = referral.get("status") or referral.get("state")
    
    # Try to find existing referral
    existing = (
        db.query(PartnerCenterReferral)
        .filter(PartnerCenterReferral.referral_id == str(referral_id))
        .first()
    )
    
    if existing:
        # Update existing
        existing.referral_type = referral_type
        existing.company_name = company_name
        existing.domain = normalized_domain
        existing.azure_tenant_id = azure_tenant_id
        existing.status = status
        existing.raw_data = referral
        # synced_at is automatically updated via server_default
        db.commit()
        db.refresh(existing)
        logger.debug(
            "partner_center_referral_updated",
            referral_id=mask_pii(str(referral_id)),
            domain=mask_pii(normalized_domain),
        )
        return existing
    else:
        # Create new
        referral_tracking = PartnerCenterReferral(
            referral_id=str(referral_id),
            referral_type=referral_type,
            company_name=company_name,
            domain=normalized_domain,
            azure_tenant_id=azure_tenant_id,
            status=status,
            raw_data=referral,
        )
        db.add(referral_tracking)
        db.commit()
        db.refresh(referral_tracking)
        logger.debug(
            "partner_center_referral_created",
            referral_id=mask_pii(str(referral_id)),
            domain=mask_pii(normalized_domain),
        )
        return referral_tracking


def trigger_domain_scan(db: Session, domain: str) -> bool:
    """
    Trigger domain scan (IDEMPOTENT - domain bazlı, referral bazlı değil).
    
    Checks if domain_signals exists for the domain. If exists, skip scan.
    If not, trigger scan_single_domain().
    
    Args:
        db: Database session
        domain: Normalized domain string
        
    Returns:
        True if scan was triggered, False if skipped (already scanned)
    """
    # Check if domain_signals exists (domain already scanned)
    existing_signal = (
        db.query(DomainSignal).filter(DomainSignal.domain == domain).first()
    )
    
    if existing_signal:
        logger.info(
            "partner_center_scan_skipped",
            domain=mask_pii(domain),
            reason="domain_already_scanned",
        )
        return False
    
    # Trigger scan
    try:
        result = scan_single_domain(domain, db, use_cache=True, commit=True)
        if result.get("success"):
            logger.info(
                "partner_center_scan_triggered",
                domain=mask_pii(domain),
                success=True,
            )
            return True
        else:
            logger.warning(
                "partner_center_scan_failed",
                domain=mask_pii(domain),
                error=result.get("error"),
            )
            return False
    except Exception as e:
        logger.error(
            "partner_center_scan_error",
            domain=mask_pii(domain),
            error=str(e),
            exc_info=True,
        )
        return False


def sync_referrals_from_partner_center(db: Session) -> Dict[str, int]:
    """
    Sync referrals from Partner Center (ana sync fonksiyonu).
    
    Flow:
    1. Partner Center'dan referral'ları çek
    2. Her referral için:
       a. Lead tipi detection
       b. Domain extraction (fallback chain)
       c. Domain yoksa → skip (log warning)
       d. raw_leads ingestion
       e. partner_center_referrals tracking
       f. Azure Tenant ID sinyali → company provider override
       g. Company upsert
       h. Domain scan trigger (idempotent - domain bazlı)
    3. Duplicate referral'ları skip et
    4. Her referral bağımsız işlenir (bir hata diğerlerini etkilemez)
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with sync statistics:
        - success_count: Number of successfully processed referrals
        - failure_count: Number of failed referrals
        - skipped_count: Number of skipped referrals (no domain, duplicates)
    """
    if not settings.partner_center_enabled:
        logger.warning("partner_center_sync_disabled")
        return {"success_count": 0, "failure_count": 0, "skipped_count": 0}
    
    try:
        # Initialize Partner Center client
        client = PartnerCenterClient()
        
        # Fetch referrals from Partner Center
        referrals = client.get_referrals()
        
        logger.info(
            "partner_center_sync_started",
            total_referrals=len(referrals),
        )
        
        success_count = 0
        failure_count = 0
        skipped_count = 0
        
        # Process each referral independently
        for referral in referrals:
            try:
                # 1. Lead tipi detection
                referral_type = detect_referral_type(referral)
                
                # 2. Domain extraction (fallback chain)
                normalized_domain = extract_domain_from_referral(referral)
                
                if not normalized_domain:
                    # Domain yoksa → skip (log warning)
                    skipped_count += 1
                    logger.warning(
                        "partner_center_referral_skipped",
                        referral_id=referral.get("id"),
                        reason="domain_not_found",
                    )
                    continue
                
                # 3. raw_leads ingestion
                ingest_to_raw_leads(db, referral, normalized_domain)
                
                # 4. partner_center_referrals tracking
                upsert_referral_tracking(db, referral, normalized_domain)
                
                # 5. Azure Tenant ID sinyali → company provider override
                azure_tenant_id = (
                    referral.get("azureTenantId") or referral.get("azure_tenant_id")
                )
                company_name = (
                    referral.get("companyName") or referral.get("company_name")
                )
                
                # 6. Company upsert (with provider override if Azure Tenant ID exists)
                provider = "M365" if azure_tenant_id else None
                company = upsert_companies(
                    db=db,
                    domain=normalized_domain,
                    company_name=company_name,
                    provider=provider,
                )
                
                # Apply Azure Tenant ID signal (if not already set)
                if azure_tenant_id and company.provider != "M365":
                    apply_azure_tenant_signal(db, company, azure_tenant_id)
                
                # 7. Domain scan trigger (idempotent - domain bazlı)
                # MVP NOTE: Scan trigger disabled for MVP safety. Manual scan via /scan/domain endpoint.
                # Uncomment when ready for automatic scanning:
                # trigger_domain_scan(db, normalized_domain)
                
                success_count += 1
                
            except IntegrityError as e:
                # Duplicate referral (referral_id unique constraint)
                skipped_count += 1
                logger.warning(
                    "partner_center_referral_duplicate",
                    referral_id=referral.get("id"),
                    error=str(e),
                )
                db.rollback()
                continue
                
            except Exception as e:
                # Bir referral'da hata olsa bile diğerleri işlenmeye devam edecek
                failure_count += 1
                logger.error(
                    "partner_center_referral_error",
                    referral_id=referral.get("id"),
                    error=str(e),
                    exc_info=True,
                )
                db.rollback()
                continue
        
        logger.info(
            "partner_center_sync_completed",
            success_count=success_count,
            failure_count=failure_count,
            skipped_count=skipped_count,
        )
        
        return {
            "success_count": success_count,
            "failure_count": failure_count,
            "skipped_count": skipped_count,
        }
        
    except Exception as e:
        logger.error(
            "partner_center_sync_failed",
            error=str(e),
            exc_info=True,
        )
        return {"success_count": 0, "failure_count": 0, "skipped_count": 0}

