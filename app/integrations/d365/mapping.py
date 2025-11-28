"""Hunter → D365 Lead mapping functions."""

from typing import Dict, Any, Optional, List
from datetime import datetime
from app.core.logging import logger


def _map_segment_to_option_set_value(segment: Optional[str]) -> Optional[int]:
    """
    Map Hunter segment to D365 Option Set integer value.
    
    ⚠️ NOTE: D365'teki hnt_segment field'ı SMB/MidMarket/Enterprise değerlerini kullanıyor,
    ama Hunter'da Migration/Existing/Cold/Skip segment'leri var. Bu uyuşmuyor!
    
    Şimdilik None döndürüyoruz - segment mapping'i gelecekte düzeltilmeli.
    
    D365 Option Set values (actual from D365):
    - SMB: 816940000
    - MidMarket: 816940001
    - Enterprise: 816940002
    
    Args:
        segment: Hunter segment string (Migration, Existing, Cold, Skip)
        
    Returns:
        Option Set integer value or None (currently always None - mapping mismatch)
    """
    # TODO: Hunter segment (Migration/Existing/Cold/Skip) ile D365 segment (SMB/MidMarket/Enterprise)
    # uyuşmuyor. Bu mapping gelecekte düzeltilmeli veya segment field'ı kullanılmamalı.
    # Şimdilik None döndürüyoruz.
    return None


def _map_tenant_size_to_option_set_value(tenant_size: Optional[str]) -> Optional[int]:
    """
    Map Hunter tenant_size to D365 Option Set integer value.
    
    D365 Option Set values (actual from D365):
    - Small (1-50): 816940000
    - Medium (51-250): 816940001
    - Large (251-1000): 816940002
    - Enterprise (1000+): 816940003
    
    Args:
        tenant_size: Hunter tenant_size string (small, medium, large)
        
    Returns:
        Option Set integer value or None
    """
    if not tenant_size:
        return None
    
    # Normalize to lowercase
    tenant_size_lower = tenant_size.lower()
    
    # Map to D365 Option Set values
    mapping = {
        "small": 816940000,  # Small (1-50)
        "medium": 816940001,  # Medium (51-250)
        "large": 816940002,  # Large (251-1000)
        # Note: Enterprise (1000+) = 816940003, but Hunter doesn't have this value
    }
    
    return mapping.get(tenant_size_lower)


def _map_source_to_option_set_value(source: Optional[str]) -> Optional[int]:
    """
    Map Hunter source to D365 Option Set integer value.
    
    D365 Option Set values (actual from D365):
    - Partner Center: 816940000
    - Manual: 816940001
    - Import: 816940002
    - Other: 816940003
    
    Args:
        source: Hunter source string (Manual, Partner Center, Import)
        
    Returns:
        Option Set integer value or None
    """
    if not source:
        return None
    
    # Map to D365 Option Set values
    mapping = {
        "Partner Center": 816940000,
        "Manual": 816940001,
        "Import": 816940002,
        # Note: "Other" = 816940003, but Hunter doesn't use this value
    }
    
    return mapping.get(source)


def _map_processing_status_to_option_set_value(status: Optional[str]) -> Optional[int]:
    """
    Map processing status to D365 Option Set integer value.
    
    D365 Option Set values (actual from D365):
    - Idle: 816940000
    - Working: 816940001
    - Completed: 816940002
    - Error: 816940003
    
    Args:
        status: Processing status string (Idle, Working, Completed, Error)
        
    Returns:
        Option Set integer value or None
    """
    if not status:
        return None
    
    # Map to D365 Option Set values
    mapping = {
        "Idle": 816940000,
        "Working": 816940001,
        "Completed": 816940002,
        "Error": 816940003,
    }
    
    return mapping.get(status)


def map_lead_to_d365(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map Hunter lead data to D365 Lead entity (24 fields, PoC).
    
    Maps Hunter fields to D365 Lead entity using hnt_* prefix (confirmed from D365).
    Only includes fields that exist in D365 (Post-MVP: 6 fields excluded).
    
    Args:
        lead_data: Hunter lead data dictionary (from leads_ready view)
                  Expected fields:
                  - domain, canonical_name, provider, tenant_size
                  - readiness_score, segment, priority_score
                  - infrastructure_summary (from IP enrichment)
                  - contact_emails (JSONB array)
                  - referral_id, azure_tenant_id, referral_type (if from Partner Center)
                  - d365_sync_attempt_count, d365_sync_last_at, d365_sync_error, d365_sync_status
        
    Returns:
        D365 Lead entity payload (ready for D365 Web API)
        
    Note:
        Post-MVP fields (excluded from PoC):
        - priority_category, priority_label, technical_heat
        - commercial_segment, commercial_heat
        - is_partner_center_referral (calculated from referral_id)
    """
    domain = lead_data.get("domain", "")
    if not domain:
        raise ValueError("Domain is required for D365 mapping")
    
    company_name = lead_data.get("canonical_name") or lead_data.get("company_name") or domain
    
    # Build D365 Lead payload
    d365_payload = {
        # Basic D365 Lead fields
        "subject": f"Hunter: {domain}",
        "companyname": company_name,
        "websiteurl": f"https://{domain}" if domain else None,
    }
    
    # Add email if available (from contact_emails JSONB array)
    primary_email = _extract_primary_email(lead_data)
    if primary_email:
        d365_payload["emailaddress1"] = primary_email
    
    # Hunter custom fields (D365 uses hnt_* prefix - confirmed from LEAD-DATA-DICTIONARY.md)
    # Only include fields that exist in D365 (24 fields, Post-MVP: 6 fields excluded)
    hunter_fields = {
        # Hunter Intelligence Fields (Section 2)
        "hnt_finalscore": lead_data.get("readiness_score"),  # Hunter Final Score
        "hnt_priorityscore": lead_data.get("priority_score"),  # Hunter Priority Score (1-7)
        # hnt_segment: EXCLUDED - Hunter segment (Migration/Existing/Cold/Skip) ile D365 segment (SMB/MidMarket/Enterprise) uyuşmuyor
        # TODO: Segment mapping'i gelecekte düzeltilmeli veya segment field'ı kullanılmamalı
        "hnt_provider": lead_data.get("provider"),  # Hunter Provider
        "hnt_huntertenantsize": _map_tenant_size_to_option_set_value(lead_data.get("tenant_size")),  # Hunter Tenant Size (Option Set - mapped to integer)
        "hnt_infrasummary": lead_data.get("infrastructure_summary"),  # Hunter Infrastructure Summary
        
        # Post-MVP: Excluded fields (not in D365 yet):
        # - hnt_prioritycategory (priority_category)
        # - hnt_prioritylabel (priority_label)
        # - hnt_technicalheat (technical_heat)
        # - hnt_commercialsegment (commercial_segment)
        # - hnt_commercialheat (commercial_heat)
        # - hnt_ispartnercenterreferral (calculated from hnt_referralid)
    }
    
    # Partner Center Fields (Section 3)
    referral_id = lead_data.get("referral_id")
    if referral_id:
        hunter_fields["hnt_referralid"] = referral_id  # Hunter Referral ID
    
    azure_tenant_id = lead_data.get("azure_tenant_id")
    if azure_tenant_id:
        hunter_fields["hnt_tenantid"] = azure_tenant_id  # Hunter Tenant ID
    
    referral_type = lead_data.get("referral_type")
    if referral_type:
        # "hnt_referraltype": referral_type  # Hunter Referral Type (Option Set - needs value mapping)
        # TODO: Add referral_type to Option Set value mapping when values are known
        pass
    
    # Hunter Source (calculated) - Option Set with integer mapping
    source_value = "Partner Center" if referral_id else "Manual"
    source_option_value = _map_source_to_option_set_value(source_value)
    if source_option_value is not None:
        hunter_fields["hnt_source"] = source_option_value  # Hunter Source (Option Set - mapped to integer)
    
    # Hunter Processing Status (Option Set - mapped to integer)
    processing_status_str = _map_processing_status(lead_data.get("d365_sync_status"))
    processing_status_value = _map_processing_status_to_option_set_value(processing_status_str)
    if processing_status_value is not None:
        hunter_fields["hnt_processingstatus"] = processing_status_value  # Hunter Processing Status (Option Set - mapped to integer)
    
    # Hunter M365 Fit Score (if provider is M365)
    provider = lead_data.get("provider")
    if provider == "M365":
        readiness_score = lead_data.get("readiness_score")
        if readiness_score is not None:
            hunter_fields["hnt_m365fitscore"] = readiness_score
    
    # Sync & Operations Fields (Section 4)
    sync_attempt_count = lead_data.get("d365_sync_attempt_count")
    if sync_attempt_count is not None:
        hunter_fields["hnt_syncattemptcount"] = sync_attempt_count  # Hunter Sync Attempt Count
    
    last_sync_time = lead_data.get("d365_sync_last_at")
    if last_sync_time:
        # Convert datetime to ISO format string for JSON serialization
        if isinstance(last_sync_time, datetime):
            hunter_fields["hnt_lastsynctime"] = last_sync_time.isoformat()  # Hunter Last Sync Time
        elif isinstance(last_sync_time, str):
            # Already a string, use as-is
            hunter_fields["hnt_lastsynctime"] = last_sync_time
        else:
            # Try to convert to string
            hunter_fields["hnt_lastsynctime"] = str(last_sync_time)
    
    sync_error = lead_data.get("d365_sync_error")
    if sync_error:
        hunter_fields["hnt_syncerrormessage"] = sync_error  # Hunter Sync Error Message
    
    # processing_status = _map_processing_status(lead_data.get("d365_sync_status"))
    # if processing_status:
    #     hunter_fields["hnt_processingstatus"] = processing_status  # Hunter Processing Status (Option Set - needs value mapping)
    # Temporarily excluded - Option Set requires integer value
    
    # Note: hnt_d365leadid is set after push (from D365 response), not in mapping
    # Note: hnt_pushstatus is calculated, not in mapping
    # Note: hnt_confidence is calculated (Post-MVP enhancement)
    
    # Only include non-None fields
    for key, value in hunter_fields.items():
        if value is not None:
            d365_payload[key] = value
    
    logger.debug(
        "d365_mapping",
        message="Mapped Hunter lead to D365 payload",
        domain=domain,
        company_name=company_name,
        has_email=bool(primary_email),
        hunter_fields_count=len([v for v in hunter_fields.values() if v is not None])
    )
    
    return d365_payload


def _map_processing_status(sync_status: Optional[str]) -> Optional[str]:
    """
    Map D365 sync status to processing status enum.
    
    Maps:
    - pending → Idle
    - in_progress → Working
    - synced → Completed
    - error → Error
    
    Args:
        sync_status: D365 sync status from companies table
        
    Returns:
        Processing status string (Idle, Working, Completed, Error) or None
    """
    if not sync_status:
        return "Idle"
    
    mapping = {
        "pending": "Idle",
        "in_progress": "Working",
        "synced": "Completed",
        "error": "Error",
    }
    
    return mapping.get(sync_status, "Idle")


def _extract_primary_email(lead_data: Dict[str, Any]) -> Optional[str]:
    """
    Extract primary email from lead data.
    
    Tries multiple sources:
    1. contact_emails JSONB array (first email)
    2. primary_email field (if exists)
    3. email field (if exists)
    
    Args:
        lead_data: Hunter lead data dictionary
        
    Returns:
        Primary email address or None
    """
    # Try contact_emails JSONB array (from companies table)
    contact_emails = lead_data.get("contact_emails")
    if contact_emails:
        if isinstance(contact_emails, list) and len(contact_emails) > 0:
            # Get first email from array
            first_email = contact_emails[0]
            if isinstance(first_email, dict):
                # If it's a dict with 'email' key
                return first_email.get("email") or first_email.get("value")
            elif isinstance(first_email, str):
                return first_email
    
    # Try direct email fields
    return (
        lead_data.get("primary_email") or
        lead_data.get("email") or
        None
    )

