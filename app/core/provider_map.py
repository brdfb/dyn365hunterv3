"""Provider mapping utilities."""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path


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


def classify_provider(mx_root: Optional[str]) -> str:
    """
    Classify a mail provider based on MX root domain.

    Args:
        mx_root: Root domain of MX record (e.g., "outlook.com", "aspmx.l.google.com")
                If None or empty, returns "Unknown"

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
                return provider_name

            # Check if mx_root ends with the provider root (for subdomains)
            # e.g., "outlook-com.olc.protection.outlook.com" should match "protection.outlook.com"
            if mx_root.endswith("." + root.lower()):
                return provider_name

            # Check if provider root is contained in mx_root
            # e.g., "mail.outlook.com" should match "outlook.com"
            if "." + root.lower() in mx_root or mx_root.startswith(root.lower() + "."):
                return provider_name

    # If no match found, check if it's a local/custom mail server
    # Local mail servers typically have the domain itself or mail.{domain}
    # We'll classify as "Local" if it doesn't match any known provider
    # Otherwise, return "Unknown"

    # For now, if it doesn't match any provider, return "Local"
    # (This can be refined later based on actual patterns)
    return "Local"
