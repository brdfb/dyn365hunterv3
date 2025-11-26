"""Partner Center referral ingestion module."""

import structlog
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.models import RawLead, Company, PartnerCenterReferral, DomainSignal
from app.core.partner_center import PartnerCenterClient
from app.core.normalizer import (
    normalize_domain,
    extract_domain_from_email,
    extract_domain_from_website,
    is_valid_domain,
)
from app.core.merger import upsert_companies
from app.core.tasks import scan_single_domain
from app.config import settings
from app.core.logging import logger, mask_pii

logger = structlog.get_logger(__name__)


# Consumer domains to filter out
CONSUMER_DOMAINS = {
    "gmail.com",
    "outlook.com",
    "hotmail.com",
    "yahoo.com",
    "yahoo.co.uk",
    "ymail.com",
    "aol.com",
    "icloud.com",
    "me.com",
    "mac.com",
    "live.com",
    "msn.com",
    "protonmail.com",
    "proton.me",
    "zoho.com",
    "mail.com",
    "yandex.com",
    "gmx.com",
}


def is_consumer_domain(domain: str) -> bool:
    """
    Check if a domain is a consumer email provider domain.
    
    Args:
        domain: Domain string to check
        
    Returns:
        True if domain is a consumer email provider, False otherwise
    """
    if not domain:
        return False
    
    domain_lower = domain.lower().strip()
    return domain_lower in CONSUMER_DOMAINS


@dataclass
class PartnerCenterReferralDTO:
    """
    Partner Center Referral Data Transfer Object.
    
    Maps Microsoft Partner Center referral schema to internal DTO.
    """
    id: str
    engagement_id: Optional[str] = None
    name: Optional[str] = None
    created_date_time: Optional[datetime] = None
    updated_date_time: Optional[datetime] = None
    status: Optional[str] = None
    substatus: Optional[str] = None
    type: Optional[str] = None
    qualification: Optional[str] = None
    direction: Optional[str] = None
    customer_name: Optional[str] = None
    customer_country: Optional[str] = None
    deal_value: Optional[float] = None
    currency: Optional[str] = None
    customer_profile: Optional[Dict[str, Any]] = None
    details: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_dict(cls, referral: Dict[str, Any]) -> "PartnerCenterReferralDTO":
        """
        Create DTO from Partner Center referral dictionary.
        
        Args:
            referral: Partner Center referral dictionary
            
        Returns:
            PartnerCenterReferralDTO instance
        """
        customer_profile = referral.get("customerProfile") or {}
        details = referral.get("details") or {}
        address = customer_profile.get("address") or {}
        
        # Parse datetime strings if present
        created_date_time = None
        updated_date_time = None
        if referral.get("createdDateTime"):
            try:
                created_date_time = datetime.fromisoformat(
                    referral["createdDateTime"].replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                pass
        if referral.get("updatedDateTime"):
            try:
                updated_date_time = datetime.fromisoformat(
                    referral["updatedDateTime"].replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                pass
        
        return cls(
            id=str(referral.get("id", "")),
            engagement_id=referral.get("engagementId"),
            name=referral.get("name"),
            created_date_time=created_date_time,
            updated_date_time=updated_date_time,
            status=referral.get("status"),
            substatus=referral.get("substatus"),
            type=referral.get("type"),
            qualification=referral.get("qualification"),
            direction=referral.get("direction"),
            customer_name=customer_profile.get("name"),
            customer_country=address.get("country"),
            deal_value=details.get("dealValue"),
            currency=details.get("currency"),
            customer_profile=customer_profile,
            details=details,
        )


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
    
    Fallback chain (per design doc):
    1. CustomerProfile.Team member emails → extract domain, filter consumer domains
    2. customerProfile.ids.External (if applicable)
    3. Legacy fallback: website → email (for backward compatibility)
    4. Skip: Domain yoksa → None (log warning)
    
    Args:
        referral: Partner Center referral dictionary
        
    Returns:
        Normalized domain string, or None if not found
    """
    customer_profile = referral.get("customerProfile") or {}
    
    # 1. Try CustomerProfile.Team member emails
    team = customer_profile.get("team") or []
    if isinstance(team, list):
        candidate_emails = []
        for member in team:
            if isinstance(member, dict):
                email = member.get("email")
                if email:
                    candidate_emails.append(email)
        
        # Extract domains from emails and filter consumer domains
        for email in candidate_emails:
            domain = extract_domain_from_email(email)
            if domain:
                normalized = normalize_domain(domain)
                if normalized and not is_consumer_domain(normalized):
                    logger.debug(
                        "partner_center_domain_extracted",
                        source="customer_profile_team",
                        domain=mask_pii(normalized),
                        email=mask_pii(email),
                    )
                    return normalized
    
    # 2. Try customerProfile.ids.External (if applicable)
    ids = customer_profile.get("ids") or {}
    external_id = ids.get("External")
    if external_id:
        # External ID might be a domain or URL
        domain = extract_domain_from_website(str(external_id)) or extract_domain_from_email(str(external_id))
        if domain:
            normalized = normalize_domain(domain)
            if normalized and not is_consumer_domain(normalized):
                logger.debug(
                    "partner_center_domain_extracted",
                    source="customer_profile_ids_external",
                    domain=mask_pii(normalized),
                )
                return normalized
    
    # 3. URL-based domain extraction (Phase 3.3)
    # Check multiple URL fields in order of preference
    url_fields = [
        customer_profile.get("website"),  # customerProfile.website (preferred)
        customer_profile.get("companyWebsite"),  # customerProfile.companyWebsite
        referral.get("website"),  # Top-level website
        referral.get("companyWebsite"),  # Top-level companyWebsite
        (referral.get("details") or {}).get("website"),  # details.website
    ]
    
    for website in url_fields:
        if website:
            domain = extract_domain_from_website(website)
            if domain:
                normalized = normalize_domain(domain)
                if normalized and is_valid_domain(normalized):
                    logger.debug(
                        "partner_center_domain_extracted",
                        source="url_based",
                        domain=mask_pii(normalized),
                        url_field=mask_pii(website),
                    )
                    return normalized
    
    contact = referral.get("contact") or {}
    email = contact.get("email") or referral.get("email")
    if email:
        domain = extract_domain_from_email(email)
        if domain:
            normalized = normalize_domain(domain)
            if normalized and not is_consumer_domain(normalized):
                logger.debug(
                    "partner_center_domain_extracted",
                    source="email",
                    domain=mask_pii(normalized),
                )
                return normalized
    
    # 4. Skip (domain not found)
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
    
    Uses ON CONFLICT (referral_id) DO UPDATE strategy:
    - Update: status, substatus, updatedDateTime, deal_value (if schema supports)
    - Idempotent: re-fetch same referral updates existing record
    
    Args:
        db: Database session
        referral: Partner Center referral dictionary
        normalized_domain: Normalized domain string
        
    Returns:
        Created or updated PartnerCenterReferral instance
    """
    # Convert to DTO for consistent field extraction
    dto = PartnerCenterReferralDTO.from_dict(referral)
    
    referral_id = dto.id
    if not referral_id:
        raise ValueError("Referral ID not found in referral data")
    
    referral_type = detect_referral_type(referral)
    company_name = dto.customer_name or referral.get("companyName") or referral.get("company_name")
    azure_tenant_id = referral.get("azureTenantId") or referral.get("azure_tenant_id")
    status = dto.status or referral.get("status") or referral.get("state")
    substatus = dto.substatus
    
    # Try to find existing referral
    existing = (
        db.query(PartnerCenterReferral)
        .filter(PartnerCenterReferral.referral_id == str(referral_id))
        .first()
    )
    
    # Extract additional fields from DTO
    engagement_id = dto.engagement_id
    external_reference_id = None  # Not in current API response, reserved for future
    referral_type_api = dto.type  # API type field (different from referral_type which is our internal mapping)
    qualification = dto.qualification
    direction = dto.direction
    customer_name = dto.customer_name
    customer_country = dto.customer_country
    deal_value = dto.deal_value
    currency = dto.currency
    
    if existing:
        # Update existing (Phase 4.2: Upsert Strategy)
        # Update: status, substatus, updatedDateTime, deal_value
        existing.engagement_id = engagement_id
        existing.external_reference_id = external_reference_id
        existing.referral_type = referral_type
        existing.type = referral_type_api
        existing.qualification = qualification
        existing.direction = direction
        existing.company_name = company_name
        existing.customer_name = customer_name
        existing.customer_country = customer_country
        existing.domain = normalized_domain
        existing.azure_tenant_id = azure_tenant_id
        existing.status = status
        existing.substatus = substatus
        existing.deal_value = deal_value
        existing.currency = currency
        existing.raw_data = referral  # Always update raw_data with latest
        # synced_at is automatically updated via server_default
        db.commit()
        db.refresh(existing)
        logger.debug(
            "partner_center_referral_updated",
            referral_id=mask_pii(str(referral_id)),
            domain=mask_pii(normalized_domain),
            status=status,
            substatus=substatus,
        )
        return existing
    else:
        # Create new
        referral_tracking = PartnerCenterReferral(
            referral_id=str(referral_id),
            engagement_id=engagement_id,
            external_reference_id=external_reference_id,
            referral_type=referral_type,
            type=referral_type_api,
            qualification=qualification,
            direction=direction,
            company_name=company_name,
            customer_name=customer_name,
            customer_country=customer_country,
            domain=normalized_domain,
            azure_tenant_id=azure_tenant_id,
            status=status,
            substatus=substatus,
            deal_value=deal_value,
            currency=currency,
            raw_data=referral,
        )
        db.add(referral_tracking)
        db.commit()
        db.refresh(referral_tracking)
        logger.debug(
            "partner_center_referral_created",
            referral_id=mask_pii(str(referral_id)),
            domain=mask_pii(normalized_domain),
            status=status,
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
        
        # Metrics tracking
        total_fetched = len(referrals)
        total_processed = 0
        total_skipped = 0
        total_inserted = 0
        skipped_reasons = {
            "domain_not_found": 0,
            "duplicate": 0,
            "direction_outgoing": 0,
            "status_closed": 0,
            "substatus_excluded": 0,
        }
        
        logger.info(
            "partner_center_sync_started",
            total_fetched=total_fetched,
        )
        
        # Process each referral independently
        for referral in referrals:
            try:
                # 1. Ingestion Filter Rules (Phase 4.3)
                # Only process if:
                # - direction = 'Incoming'
                # - status IN ('New', 'Active')
                # - substatus NOT IN ('Declined','Lost','Expired','Error')
                # - domain IS NOT NULL (checked later)
                
                direction = referral.get("direction")
                status = referral.get("status")
                substatus = referral.get("substatus")
                
                # Filter: direction must be 'Incoming'
                if direction != "Incoming":
                    total_skipped += 1
                    skipped_reasons.setdefault("direction_outgoing", 0)
                    skipped_reasons["direction_outgoing"] += 1
                    logger.warning(
                        "partner_center_referral_skipped",
                        referral_id=referral.get("id"),
                        reason="direction_outgoing",
                        direction=direction,
                    )
                    continue
                
                # Filter: status must be 'New' or 'Active'
                if status not in ("New", "Active"):
                    total_skipped += 1
                    skipped_reasons.setdefault("status_closed", 0)
                    skipped_reasons["status_closed"] += 1
                    logger.warning(
                        "partner_center_referral_skipped",
                        referral_id=referral.get("id"),
                        reason="status_closed",
                        status=status,
                    )
                    continue
                
                # Filter: substatus must NOT be in excluded list
                excluded_substatuses = {"Declined", "Lost", "Expired", "Error"}
                if substatus in excluded_substatuses:
                    total_skipped += 1
                    skipped_reasons.setdefault("substatus_excluded", 0)
                    skipped_reasons["substatus_excluded"] += 1
                    logger.warning(
                        "partner_center_referral_skipped",
                        referral_id=referral.get("id"),
                        reason="substatus_excluded",
                        substatus=substatus,
                    )
                    continue
                
                # 2. Lead tipi detection
                referral_type = detect_referral_type(referral)
                
                # 3. Domain extraction (fallback chain)
                normalized_domain = extract_domain_from_referral(referral)
                
                if not normalized_domain:
                    # Domain yoksa → skip (log warning)
                    total_skipped += 1
                    skipped_reasons["domain_not_found"] += 1
                    logger.warning(
                        "partner_center_referral_skipped",
                        referral_id=referral.get("id"),
                        reason="domain_not_found",
                    )
                    continue
                
                # 4. raw_leads ingestion
                ingest_to_raw_leads(db, referral, normalized_domain)
                
                # 5. partner_center_referrals tracking
                upsert_referral_tracking(db, referral, normalized_domain)
                
                # 6. Azure Tenant ID sinyali → company provider override
                azure_tenant_id = (
                    referral.get("azureTenantId") or referral.get("azure_tenant_id")
                )
                company_name = (
                    referral.get("companyName") or referral.get("company_name")
                )
                
                # 7. Company upsert (with provider override if Azure Tenant ID exists)
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
                
                # 8. Domain scan trigger (idempotent - domain bazlı)
                # MVP NOTE: Scan trigger disabled for MVP safety. Manual scan via /scan/domain endpoint.
                # Uncomment when ready for automatic scanning:
                # trigger_domain_scan(db, normalized_domain)
                
                # Successfully ingested
                total_inserted += 1
                total_processed += 1
                
                logger.info(
                    "partner_center_referral_ingested",
                    referral_id=referral.get("id"),
                    domain=mask_pii(normalized_domain),
                    referral_type=referral_type,
                )
                
            except IntegrityError as e:
                # Duplicate referral (referral_id unique constraint)
                total_skipped += 1
                skipped_reasons["duplicate"] += 1
                logger.warning(
                    "partner_center_referral_skipped",
                    referral_id=referral.get("id"),
                    reason="duplicate",
                    error=str(e),
                )
                db.rollback()
                continue
                
            except Exception as e:
                # Bir referral'da hata olsa bile diğerleri işlenmeye devam edecek
                total_processed += 1  # Count as processed (attempted)
                logger.error(
                    "partner_center_referral_error",
                    referral_id=referral.get("id"),
                    error=str(e),
                    exc_info=True,
                )
                db.rollback()
                continue
        
        # Summary log with all metrics
        logger.info(
            "partner_center_sync_summary",
            total_fetched=total_fetched,
            total_processed=total_processed,
            total_inserted=total_inserted,
            total_skipped=total_skipped,
            skipped_no_domain=skipped_reasons["domain_not_found"],
            skipped_duplicate=skipped_reasons["duplicate"],
            skipped_direction_outgoing=skipped_reasons.get("direction_outgoing", 0),
            skipped_status_closed=skipped_reasons.get("status_closed", 0),
            skipped_substatus_excluded=skipped_reasons.get("substatus_excluded", 0),
            failure_count=total_processed - total_inserted,
        )
        
        return {
            "success_count": total_inserted,
            "failure_count": total_processed - total_inserted,
            "skipped_count": total_skipped,
        }
        
    except Exception as e:
        logger.error(
            "partner_center_sync_failed",
            error=str(e),
            exc_info=True,
        )
        return {"success_count": 0, "failure_count": 0, "skipped_count": 0}

