"""Partner Center referral ingestion module."""

import structlog
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from urllib.parse import urlparse
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
    
    Enhanced detection: Checks multiple fields and locations in the referral structure.
    
    Args:
        referral: Partner Center referral dictionary
        
    Returns:
        Referral type: 'co-sell', 'marketplace', 'solution-provider', or None
    """
    # Try multiple locations for referral type (Partner Center API structure varies)
    # 1. Top-level 'type' field
    referral_type = referral.get("type")
    
    # 2. Top-level 'referralType' field (alternative naming)
    if not referral_type:
        referral_type = referral.get("referralType")
    
    # 3. Details.type (some referral structures have type in details)
    if not referral_type:
        details = referral.get("details") or {}
        referral_type = details.get("type")
    
    # 4. Category field (sometimes used instead of type)
    if not referral_type:
        referral_type = referral.get("category")
    
    # 5. Source field (sometimes contains type information)
    if not referral_type:
        source = referral.get("source")
        if source and isinstance(source, str):
            # Check if source contains type keywords
            source_lower = source.lower()
            if "co-sell" in source_lower or "cosell" in source_lower:
                return "co-sell"
            elif "marketplace" in source_lower:
                return "marketplace"
            elif "solution" in source_lower or "provider" in source_lower:
                return "solution-provider"
    
    # If still no type found, return None
    if not referral_type:
        return None
    
    # Normalize and map to internal types
    referral_type_lower = str(referral_type).lower()
    
    # Map Partner Center types to our internal types
    # Co-sell variations
    if "co-sell" in referral_type_lower or "cosell" in referral_type_lower or "co_sell" in referral_type_lower:
        return "co-sell"
    # Marketplace variations
    elif "marketplace" in referral_type_lower or "market_place" in referral_type_lower:
        return "marketplace"
    # Solution Provider variations
    elif "solution" in referral_type_lower and "provider" in referral_type_lower:
        return "solution-provider"
    elif "solution-provider" in referral_type_lower or "solution_provider" in referral_type_lower:
        return "solution-provider"
    elif referral_type_lower == "sp":
        return "solution-provider"
    
    return None


def extract_domain_from_referral(referral: Dict[str, Any]) -> Optional[str]:
    """
    Extract domain from referral using fallback chain.
    
    Fallback chain (updated 2025-01-30):
    1. Contact email (referral.contact.email) → extract domain, filter consumer domains
    2. CustomerProfile.Team member emails → extract domain, filter consumer domains
    3. customerProfile.ids.External (if applicable)
    4. URL-based domain extraction (website fields)
    5. Top-level email (referral.email) → extract domain, filter consumer domains
    6. Skip: Domain yoksa → None (log warning)
    
    NOTE: Contact email moved to priority 1 (2025-01-30) - most reliable source for domain extraction.
    
    Args:
        referral: Partner Center referral dictionary
        
    Returns:
        Normalized domain string, or None if not found
    """
    customer_profile = referral.get("customerProfile") or {}
    
    # 1. Try Contact email first (highest priority - updated 2025-01-30)
    # Contact email is the most reliable source as shown in Partner Center UI
    contact = referral.get("contact") or {}
    contact_email = contact.get("email")
    if contact_email:
        domain = extract_domain_from_email(contact_email)
        if domain:
            normalized = normalize_domain(domain)
            if normalized and not is_consumer_domain(normalized):
                logger.debug(
                    "partner_center_domain_extracted",
                    source="contact_email",
                    domain=mask_pii(normalized),
                    email=mask_pii(contact_email),
                )
                return normalized
    
    # 2. Try CustomerProfile.Team member emails
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
    
    # 3. Try customerProfile.ids.External (if applicable)
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
    
    # 4. URL-based domain extraction (Phase 3.3)
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
    
    # 5. Try top-level email (referral.email) as last resort
    top_level_email = referral.get("email")
    if top_level_email:
        domain = extract_domain_from_email(top_level_email)
        if domain:
            normalized = normalize_domain(domain)
            if normalized and not is_consumer_domain(normalized):
                logger.debug(
                    "partner_center_domain_extracted",
                    source="top_level_email",
                    domain=mask_pii(normalized),
                    email=mask_pii(top_level_email),
                )
                return normalized
    
    # 4. Skip (domain not found)
    logger.warning("partner_center_domain_not_found", referral_id=referral.get("id"))
    return None


def extract_raw_domain_from_referral(referral: Dict[str, Any]) -> Optional[str]:
    """
    Extract raw (non-normalized) domain from referral for debugging/storage.
    
    Phase 1: Store original domain value before normalization.
    This helps debug normalization issues and preserves original data.
    
    Args:
        referral: Partner Center referral dictionary
        
    Returns:
        Raw domain string (from website or email), or None if not found
    """
    customer_profile = referral.get("customerProfile") or {}
    
    # Try website fields first
    url_fields = [
        customer_profile.get("website"),
        customer_profile.get("companyWebsite"),
        referral.get("website"),
        referral.get("companyWebsite"),
        (referral.get("details") or {}).get("website"),
    ]
    
    for website in url_fields:
        if website:
            # Extract domain without normalization
            try:
                if not website.startswith(("http://", "https://")):
                    website = "http://" + website
                parsed = urlparse(website)
                domain = parsed.netloc or parsed.path.split("/")[0]
                if ":" in domain:
                    domain = domain.split(":")[0]
                if domain:
                    return domain.strip()
            except Exception:
                # If parsing fails, return as-is (might be just a domain)
                return website.strip() if website else None
    
    # Try contact email first (updated 2025-01-30 - higher priority)
    contact = referral.get("contact") or {}
    contact_email = contact.get("email")
    if contact_email and "@" in contact_email:
        return contact_email.split("@")[-1].strip()
    
    # Try top-level email as fallback
    top_level_email = referral.get("email")
    if top_level_email and "@" in top_level_email:
        return top_level_email.split("@")[-1].strip()
    
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
    db: Session, referral: Dict[str, Any], normalized_domain: Optional[str], raw_domain: Optional[str] = None
) -> PartnerCenterReferral:
    """
    Upsert referral tracking in partner_center_referrals table.
    
    Phase 1: Now accepts nullable domain - all referrals are saved regardless of domain extraction.
    
    Uses ON CONFLICT (referral_id) DO UPDATE strategy:
    - Update: status, substatus, updatedDateTime, deal_value (if schema supports)
    - Idempotent: re-fetch same referral updates existing record
    
    Args:
        db: Database session
        referral: Partner Center referral dictionary
        normalized_domain: Normalized domain string (nullable in Phase 1)
        raw_domain: Original domain before normalization (optional, for debugging)
        
    Returns:
        Created or updated PartnerCenterReferral instance
        
    Note:
        link_status and linked_lead_id are set by sync_referrals_from_partner_center(),
        not by this function.
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
        existing.domain = normalized_domain  # Can be NULL in Phase 1
        existing.raw_domain = raw_domain  # Phase 1: Store original domain
        existing.azure_tenant_id = azure_tenant_id
        existing.status = status
        existing.substatus = substatus
        existing.deal_value = deal_value
        existing.currency = currency
        existing.raw_data = referral  # Always update raw_data with latest
        # Note: link_status and linked_lead_id are set by sync function, not here
        # synced_at is automatically updated via server_default
        db.commit()
        db.refresh(existing)
        logger.debug(
            "partner_center_referral_updated",
            referral_id=mask_pii(str(referral_id)),
            domain=mask_pii(normalized_domain) if normalized_domain else None,
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
            domain=normalized_domain,  # Can be NULL in Phase 1
            raw_domain=raw_domain,  # Phase 1: Store original domain
            azure_tenant_id=azure_tenant_id,
            status=status,
            substatus=substatus,
            deal_value=deal_value,
            currency=currency,
            raw_data=referral,
            # Note: link_status and linked_lead_id are set by sync function, not here
        )
        db.add(referral_tracking)
        db.commit()
        db.refresh(referral_tracking)
        logger.debug(
            "partner_center_referral_created",
            referral_id=mask_pii(str(referral_id)),
            domain=mask_pii(normalized_domain) if normalized_domain else None,
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
    
    Phase 1: REVISED - All referrals are saved, regardless of domain extraction.
    
    Flow:
    1. Partner Center'dan referral'ları çek
    2. Her referral için (filter rules geçerse):
       a. Lead tipi detection
       b. Domain extraction (fallback chain)
       c. Raw domain extraction (for debugging)
       d. partner_center_referrals tracking (ALWAYS - domain olsun olmasın)
       e. If domain exists:
          - Check if company exists → set link_status
          - raw_leads ingestion (existing flow)
          - Company upsert (existing flow)
          - Azure Tenant ID sinyali (existing flow)
       f. If domain doesn't exist:
          - link_status = 'unlinked'
          - Skip raw_leads/company ingestion (Phase 1: no auto-ingest)
    3. Duplicate referral'ları skip et (IntegrityError)
    4. Her referral bağımsız işlenir (bir hata diğerlerini etkilemez)
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with sync statistics:
        - success_count: Number of successfully processed referrals
        - failure_count: Number of failed referrals
        - skipped_count: Number of skipped referrals (filter rules, duplicates)
        - total_fetched: Total referrals fetched from Partner Center
        - total_inserted: Total referrals inserted/updated in DB
    """
    if not settings.partner_center_enabled:
        logger.warning("partner_center_sync_disabled")
        return {
            "success_count": 0,
            "failure_count": 0,
            "skipped_count": 0,
            "total_fetched": 0,
            "total_inserted": 0,
        }
    
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
            "duplicate": 0,
            "direction_outgoing": 0,
            # status_closed and substatus_excluded removed (2025-01-30) - all statuses accepted
        }
        # Phase 1: domain_not_found is no longer a skip reason (referrals are saved anyway)
        
        logger.info(
            "partner_center_sync_started",
            total_fetched=total_fetched,
        )
        
        # Process each referral independently
        for referral in referrals:
            try:
                # 1. Ingestion Filter Rules (Updated 2025-01-30)
                # Only process if:
                # - direction = 'Incoming' (required)
                # - All statuses are accepted (Active, Closed, New, etc.) - filtering can be done in UI
                # - All substatuses are accepted - filtering can be done in UI
                # - Domain extraction is optional - referrals are saved even without domain (Phase 1)
                
                direction = referral.get("direction")
                status = referral.get("status")
                substatus = referral.get("substatus")
                
                # Filter: direction must be 'Incoming' (only filter - all statuses accepted)
                if direction != "Incoming":
                    total_skipped += 1
                    skipped_reasons.setdefault("direction_outgoing", 0)
                    skipped_reasons["direction_outgoing"] += 1
                    logger.debug(
                        "partner_center_referral_skipped",
                        referral_id=referral.get("id"),
                        reason="direction_outgoing",
                        direction=direction,
                    )
                    continue
                
                # Status filter removed (2025-01-30) - accept all statuses (Active, Closed, New, etc.)
                # Status filtering can be done in UI or application layer after data is stored
                
                # Substatus filter removed (2025-01-30) - accept all substatuses
                # Substatus filtering can be done in UI or application layer after data is stored
                
                # 2. Lead tipi detection
                referral_type = detect_referral_type(referral)
                
                # 3. Domain extraction (fallback chain)
                normalized_domain = extract_domain_from_referral(referral)
                
                # 4. Raw domain extraction (Phase 1: for debugging)
                raw_domain = extract_raw_domain_from_referral(referral)
                
                # 5. partner_center_referrals tracking (ALWAYS - Phase 1)
                # Domain olsun olmasın, her referral kaydedilir
                referral_tracking = upsert_referral_tracking(
                    db, referral, normalized_domain, raw_domain
                )
                
                # 6. Link status determination
                linked_company = None
                if normalized_domain:
                    # Check if company exists
                    linked_company = db.query(Company).filter(
                        Company.domain == normalized_domain
                    ).first()
                    
                    if linked_company:
                        # Domain + company match → auto_linked
                        referral_tracking.link_status = 'auto_linked'
                        referral_tracking.linked_lead_id = linked_company.id
                    else:
                        # Domain var ama company yok → unlinked
                        referral_tracking.link_status = 'unlinked'
                        referral_tracking.linked_lead_id = None
                else:
                    # Domain yok → unlinked
                    referral_tracking.link_status = 'unlinked'
                    referral_tracking.linked_lead_id = None
                
                db.commit()
                
                # 7. Existing ingestion flow (only if domain exists)
                # Phase 1: Mevcut flow'a dokunmuyoruz, sadece referral tarafındaki skip sorununu düzelttik
                if normalized_domain:
                    # raw_leads ingestion
                    ingest_to_raw_leads(db, referral, normalized_domain)
                    
                    # Azure Tenant ID sinyali → company provider override
                    azure_tenant_id = (
                        referral.get("azureTenantId") or referral.get("azure_tenant_id")
                    )
                    company_name = (
                        referral.get("companyName") or referral.get("company_name")
                    )
                    
                    # Company upsert (with provider override if Azure Tenant ID exists)
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
                    
                    # Update link_status if company was just created
                    if not linked_company:
                        # Company was just created, update referral link
                        referral_tracking.link_status = 'auto_linked'
                        referral_tracking.linked_lead_id = company.id
                        db.commit()
                    
                    # Domain scan trigger (idempotent - domain bazlı)
                    # MVP NOTE: Scan trigger disabled for MVP safety. Manual scan via /scan/domain endpoint.
                    # Uncomment when ready for automatic scanning:
                    # trigger_domain_scan(db, normalized_domain)
                    
                    # Successfully ingested
                    total_inserted += 1
                    logger.info(
                        "partner_center_referral_ingested",
                        referral_id=referral.get("id"),
                        domain=mask_pii(normalized_domain),
                        referral_type=referral_type,
                        link_status=referral_tracking.link_status,
                    )
                else:
                    # Domain yok ama referral kaydedildi (Phase 1)
                    logger.info(
                        "partner_center_referral_saved_no_domain",
                        referral_id=referral.get("id"),
                        link_status="unlinked",
                    )
                    total_inserted += 1  # Count as inserted (saved to DB)
                
                total_processed += 1
                
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
            "total_fetched": total_fetched,
            "total_inserted": total_inserted,
        }
        
    except Exception as e:
        logger.error(
            "partner_center_sync_failed",
            error=str(e),
            exc_info=True,
        )
        return {
            "success_count": 0,
            "failure_count": 0,
            "skipped_count": 0,
            "total_fetched": 0,
            "total_inserted": 0,
        }


def update_existing_referral_types(db: Session) -> Dict[str, int]:
    """
    Update referral_type for existing referrals that have raw_data but null referral_type.
    
    This is a one-time migration function to fix referral types for existing records.
    Uses the enhanced detect_referral_type() function to re-analyze raw_data.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with update statistics:
        - updated_count: Number of referrals updated
        - skipped_count: Number of referrals skipped (no raw_data or already has type)
        - error_count: Number of errors encountered
    """
    from app.db.models import PartnerCenterReferral
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    try:
        # Find all referrals with raw_data but null referral_type
        referrals = (
            db.query(PartnerCenterReferral)
            .filter(
                PartnerCenterReferral.raw_data.isnot(None),
                PartnerCenterReferral.referral_type.is_(None)
            )
            .all()
        )
        
        logger.info(
            "referral_type_update_start",
            total_referrals=len(referrals)
        )
        
        for referral in referrals:
            try:
                raw_data = referral.raw_data
                if not raw_data:
                    skipped_count += 1
                    continue
                
                # Detect referral type using enhanced function
                new_referral_type = detect_referral_type(raw_data)
                
                if new_referral_type:
                    referral.referral_type = new_referral_type
                    updated_count += 1
                    logger.debug(
                        "referral_type_updated",
                        referral_id=mask_pii(referral.referral_id),
                        referral_type=new_referral_type
                    )
                else:
                    skipped_count += 1
                    logger.debug(
                        "referral_type_not_detected",
                        referral_id=mask_pii(referral.referral_id)
                    )
            except Exception as e:
                error_count += 1
                logger.error(
                    "referral_type_update_error",
                    referral_id=mask_pii(referral.referral_id) if referral else None,
                    error=str(e),
                    exc_info=True
                )
                continue
        
        # Commit all updates
        db.commit()
        
        logger.info(
            "referral_type_update_complete",
            updated_count=updated_count,
            skipped_count=skipped_count,
            error_count=error_count
        )
        
        return {
            "updated_count": updated_count,
            "skipped_count": skipped_count,
            "error_count": error_count
        }
        
    except Exception as e:
        db.rollback()
        logger.error(
            "referral_type_update_failed",
            error=str(e),
            exc_info=True
        )
        return {
            "updated_count": updated_count,
            "skipped_count": skipped_count,
            "error_count": error_count + 1
        }

