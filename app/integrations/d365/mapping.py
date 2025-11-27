"""Hunter → D365 Lead mapping functions."""

from typing import Dict, Any, Optional, List
from app.core.logging import logger


def map_lead_to_d365(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map Hunter lead data to D365 Lead entity.
    
    Maps all relevant Hunter fields to D365 Lead entity, including:
    - Basic info (subject, company name, website, email)
    - Hunter custom fields (score, segment, priority, infrastructure, etc.)
    - Provider and tenant size information
    
    Args:
        lead_data: Hunter lead data dictionary (from leads_ready view)
                  Expected fields:
                  - domain, canonical_name, provider, tenant_size
                  - readiness_score, segment, priority_category, priority_label
                  - infrastructure_summary (from IP enrichment)
                  - contact_emails (JSONB array)
                  - referral_id (if from Partner Center)
        
    Returns:
        D365 Lead entity payload (ready for D365 Web API)
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
    
    # Hunter custom fields (these need to be created in D365 as custom fields)
    # Format: hunter_* prefix for custom fields
    hunter_fields = {
        "hunter_score": lead_data.get("readiness_score"),
        "hunter_segment": lead_data.get("segment"),
        "hunter_priority_category": lead_data.get("priority_category"),
        "hunter_priority_label": lead_data.get("priority_label"),
        "hunter_infrastructure": lead_data.get("infrastructure_summary"),
        "hunter_provider": lead_data.get("provider"),
        "hunter_tenant_size": lead_data.get("tenant_size"),
        "hunter_technical_heat": lead_data.get("technical_heat"),
        "hunter_commercial_segment": lead_data.get("commercial_segment"),
        "hunter_commercial_heat": lead_data.get("commercial_heat"),
    }
    
    # Add referral ID if available (Partner Center integration)
    referral_id = lead_data.get("referral_id")
    if referral_id:
        hunter_fields["hunter_referral_id"] = referral_id
    
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

