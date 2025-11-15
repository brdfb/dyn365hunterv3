"""Provider mapping utilities."""

import json
import os
import re
from typing import Dict, List, Optional
from pathlib import Path
from app.core.cache import get_cached_provider, set_cached_provider


_PROVIDERS_CACHE: Optional[Dict] = None


def load_providers() -> Dict:
    """
    Load provider mapping data from providers.json.

    Returns:
        Dictionary with 'providers' key containing list of provider definitions

    Raises:
        FileNotFoundError: If providers.json not found
        json.JSONDecodeError: If JSON is invalid
    """
    global _PROVIDERS_CACHE

    if _PROVIDERS_CACHE is not None:
        return _PROVIDERS_CACHE

    # Get the path to providers.json
    # This file is in app/data/providers.json
    current_dir = Path(__file__).parent.parent
    providers_path = current_dir / "data" / "providers.json"

    if not providers_path.exists():
        raise FileNotFoundError(f"providers.json not found at {providers_path}")

    with open(providers_path, "r", encoding="utf-8") as f:
        _PROVIDERS_CACHE = json.load(f)

    return _PROVIDERS_CACHE


def classify_provider(mx_root: Optional[str], use_cache: bool = True) -> str:
    """
    Classify a mail provider based on MX root domain.

    Uses Redis-based caching (24 hour TTL) to reduce repeated lookups.

    Args:
        mx_root: Root domain of MX record (e.g., "outlook.com", "aspmx.l.google.com")
                If None or empty, returns "Unknown"
        use_cache: Whether to use cache (default: True)

    Returns:
        Provider name: "M365", "Google", "Yandex", "Zoho", "Amazon",
                      "SendGrid", "Mailgun", "Hosting", "Local", or "Unknown"

    Examples:
        >>> classify_provider("outlook-com.olc.protection.outlook.com")
        'M365'
        >>> classify_provider("aspmx.l.google.com")
        'Google'
        >>> classify_provider("mail.example.com")
        'Local'
        >>> classify_provider(None)
        'Unknown'
    """
    if not mx_root:
        return "Unknown"

    mx_root = mx_root.lower().strip()

    # Check cache first
    if use_cache:
        cached_provider = get_cached_provider(mx_root)
        if cached_provider is not None:
            return cached_provider

    # Load providers
    providers_data = load_providers()
    providers = providers_data.get("providers", [])

    # Check each provider's MX roots
    for provider in providers:
        provider_name = provider.get("name", "")
        mx_roots = provider.get("mx_roots", [])

        # Check if mx_root matches any of the provider's MX roots
        for root in mx_roots:
            # Exact match
            if mx_root == root.lower():
                provider = provider_name
                # Cache result
                if use_cache:
                    set_cached_provider(mx_root, provider)
                return provider

            # Check if mx_root ends with the provider root (for subdomains)
            # e.g., "outlook-com.olc.protection.outlook.com" should match "protection.outlook.com"
            if mx_root.endswith("." + root.lower()):
                provider = provider_name
                # Cache result
                if use_cache:
                    set_cached_provider(mx_root, provider)
                return provider

            # Check if provider root is contained in mx_root
            # e.g., "mail.outlook.com" should match "outlook.com"
            if "." + root.lower() in mx_root or mx_root.startswith(root.lower() + "."):
                provider = provider_name
                # Cache result
                if use_cache:
                    set_cached_provider(mx_root, provider)
                return provider

    # If no match found, check if it's a local/custom mail server
    # Local mail servers typically have the domain itself or mail.{domain}
    # We'll classify as "Local" if it doesn't match any known provider
    # Otherwise, return "Unknown"

    # For now, if it doesn't match any provider, return "Local"
    # (This can be refined later based on actual patterns)
    provider = "Local"
    # Cache result
    if use_cache:
        set_cached_provider(mx_root, provider)
    return provider


def classify_local_provider(mx_root: Optional[str]) -> Optional[str]:
    """
    Classify local provider from MX root domain.
    
    This function identifies Turkish/local hosting providers from MX records.
    
    Args:
        mx_root: Root domain of MX record (e.g., "mail.turkhost.com.tr")
    
    Returns:
        Local provider name (e.g., "TürkHost", "Natro") or None if not recognized
    
    Examples:
        >>> classify_local_provider("mail.turkhost.com.tr")
        'TürkHost'
        >>> classify_local_provider("mail.natro.com")
        'Natro'
        >>> classify_local_provider("mail.example.com")
        None
    """
    if not mx_root:
        return None
    
    mx_lower = mx_root.lower().strip()
    
    # Load providers and get local provider mappings
    providers_data = load_providers()
    providers = providers_data.get("providers", [])
    
    # Find Local provider entry
    for provider in providers:
        if provider.get("name") == "Local":
            local_providers = provider.get("local_providers", {})
            
            # Check if mx_root contains any local provider domain
            for provider_domain, provider_name in local_providers.items():
                if provider_domain in mx_lower:
                    return provider_name
    
    return None


def estimate_tenant_size(provider: str, mx_root: Optional[str]) -> Optional[str]:
    """
    Estimate tenant size from MX pattern.
    
    This function analyzes MX patterns to estimate tenant size (small/medium/large).
    
    Args:
        provider: Provider name (e.g., "M365", "Google")
        mx_root: Root domain of MX record (e.g., "outlook-com.olc.protection.outlook.com")
    
    Returns:
        Tenant size: "small", "medium", "large", or None if cannot be determined
    
    Examples:
        >>> estimate_tenant_size("M365", "outlook-com.olc.protection.outlook.com")
        'small'
        >>> estimate_tenant_size("M365", "mail.protection.outlook.com")
        'large'
        >>> estimate_tenant_size("Google", "aspmx.l.google.com")
        'medium'
    """
    if not provider or not mx_root:
        return None
    
    mx_lower = mx_root.lower().strip()
    
    if provider == "M365":
        # Enterprise pattern (mail.protection.outlook.com)
        if "mail.protection.outlook.com" in mx_lower:
            return "large"
        
        # Regional pattern (eur05, us01, etc.)
        # Pattern: {region}{number}.protection.outlook.com
        if re.search(r'[a-z]{3}\d{2}\.protection\.outlook\.com', mx_lower):
            return "small"
        
        # OLC pattern (Office 365 Cloud)
        # Pattern: *-*.olc.protection.outlook.com
        if "olc.protection.outlook.com" in mx_lower:
            return "small"
        
        # Default for other M365 patterns
        return "medium"
    
    elif provider == "Google":
        # Default Google Workspace pattern
        if "aspmx.l.google.com" in mx_lower:
            return "medium"
        
        # Enterprise patterns (custom domains)
        # If it's Google but not standard pattern, likely enterprise
        if "google.com" in mx_lower or "googlemail.com" in mx_lower:
            return "large"
        
        return "medium"
    
    # For other providers, we don't have enough pattern data
    return None
