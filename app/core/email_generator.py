"""Generic email address generation utilities."""

from typing import List
from app.core.normalizer import normalize_domain

# Generic local parts (Türkiye + International)
GENERIC_LOCAL_PARTS = [
    "info",
    "iletisim",
    "muhasebe",
    "satis",
    "sales",
    "admin",
    "support",
    "ik",
    "hr",
]


def generate_generic_emails(domain: str) -> List[str]:
    """
    Generate generic email addresses for a domain.

    Args:
        domain: Domain name (will be normalized)

    Returns:
        List of generic email addresses (unique, sorted)

    Examples:
        >>> generate_generic_emails("example.com")
        ['admin@example.com', 'hr@example.com', 'ik@example.com', ...]
    """
    # Normalize domain
    normalized = normalize_domain(domain)
    if not normalized:
        return []

    # Generate emails
    emails = [f"{local}@{normalized}" for local in GENERIC_LOCAL_PARTS]

    # Remove duplicates and sort
    return sorted(set(emails))
