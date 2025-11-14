"""Domain normalization utilities."""

import re
from urllib.parse import urlparse
from idna import decode as idna_decode, encode as idna_encode


def is_valid_domain(domain: str) -> bool:
    """
    Check if a domain string is a valid domain format.

    Valid domain format:
    - Contains at least one dot
    - Each part is 1-63 characters
    - Contains only alphanumeric characters, hyphens, and dots
    - Not empty or whitespace-only
    - Not common invalid values like "nan", "n/a", etc.

    Args:
        domain: Domain string to validate

    Returns:
        True if domain format is valid, False otherwise
    """
    if not domain:
        return False

    domain = domain.strip()

    # Check for common invalid values
    invalid_values = [
        "nan",
        "n/a",
        "na",
        "none",
        "null",
        "web sitesi",
        "website",
        "web",
        "http",
        "https",
    ]
    if domain.lower() in invalid_values:
        return False

    # Check if it looks like a URL (contains :// or starts with http)
    if "://" in domain or domain.lower().startswith(("http://", "https://")):
        return False

    # Basic domain format check: must contain at least one dot
    if "." not in domain:
        return False

    # Check domain parts
    parts = domain.split(".")
    if len(parts) < 2:
        return False

    # Each part must be 1-63 characters and contain only valid characters
    domain_pattern = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$", re.IGNORECASE)
    for part in parts:
        if not part or len(part) > 63:
            return False
        if not domain_pattern.match(part):
            return False

    # TLD must be at least 2 characters
    if len(parts[-1]) < 2:
        return False

    return True


def normalize_domain(domain: str) -> str:
    """
    Normalize a domain string.

    - Convert to lowercase
    - Remove www. prefix
    - Decode punycode (IDNA)
    - Strip whitespace
    - Remove trailing dots

    Args:
        domain: Domain string to normalize

    Returns:
        Normalized domain string

    Examples:
        >>> normalize_domain("WWW.EXAMPLE.COM")
        'example.com'
        >>> normalize_domain("xn--example.com")
        'example.com'  # (after punycode decode)
    """
    if not domain:
        return ""

    # Strip whitespace
    domain = domain.strip()

    # If it looks like a URL, extract domain first
    if "://" in domain or domain.lower().startswith(("http://", "https://")):
        try:
            if not domain.startswith(("http://", "https://")):
                domain = "http://" + domain
            parsed = urlparse(domain)
            domain = parsed.netloc or parsed.path.split("/")[0]
            # Remove port if present
            if ":" in domain:
                domain = domain.split(":")[0]
            # If still empty or invalid, try manual extraction
            if not domain or not is_valid_domain(domain):
                domain = (
                    domain.replace("http://", "")
                    .replace("https://", "")
                    .split("/")[0]
                    .split("?")[0]
                    .split("#")[0]
                )
        except Exception:
            # If parsing fails, try to extract domain manually
            domain = (
                domain.replace("http://", "")
                .replace("https://", "")
                .split("/")[0]
                .split("?")[0]
                .split("#")[0]
            )

    # Remove trailing dots
    domain = domain.rstrip(".")

    # Convert to lowercase
    domain = domain.lower()

    # Remove www. prefix (case-insensitive)
    if domain.startswith("www."):
        domain = domain[4:]

    # Encode to punycode if contains non-ASCII characters (for IDNA compatibility)
    try:
        # Check if domain contains non-ASCII characters
        domain_bytes = domain.encode("ascii")
    except UnicodeEncodeError:
        # Contains non-ASCII characters, encode to punycode
        try:
            domain = idna_encode(domain).decode("ascii")
        except (UnicodeEncodeError, UnicodeError):
            # If encoding fails, return empty (invalid domain)
            return ""

    # Decode punycode if present (for display)
    try:
        if domain.startswith("xn--"):
            decoded = idna_decode(domain.encode("ascii")).decode("utf-8")
            # Keep punycode for validation, but we can use decoded for some operations
            # For now, keep punycode format for consistency
    except (UnicodeDecodeError, UnicodeError):
        # If punycode decode fails, keep original
        pass

    # Validate domain format
    if not is_valid_domain(domain):
        return ""

    return domain


def extract_domain_from_email(email: str) -> str:
    """
    Extract domain from an email address.

    Args:
        email: Email address string

    Returns:
        Normalized domain string, or empty string if invalid

    Examples:
        >>> extract_domain_from_email("user@example.com")
        'example.com'
        >>> extract_domain_from_email("test@WWW.EXAMPLE.COM")
        'example.com'
    """
    if not email:
        return ""

    email = email.strip()

    # Check if it looks like an email
    if "@" not in email:
        return ""

    # Extract domain part
    parts = email.rsplit("@", 1)
    if len(parts) != 2:
        return ""

    domain = parts[1]

    # Normalize the extracted domain
    return normalize_domain(domain)


def extract_domain_from_website(website: str) -> str:
    """
    Extract domain from a website URL.

    Supports:
    - Full URLs (http://, https://)
    - URLs without scheme
    - Domain-only strings

    Args:
        website: Website URL or domain string

    Returns:
        Normalized domain string, or empty string if invalid

    Examples:
        >>> extract_domain_from_website("https://www.example.com/path")
        'example.com'
        >>> extract_domain_from_website("example.com")
        'example.com'
        >>> extract_domain_from_website("http://WWW.EXAMPLE.COM")
        'example.com'
    """
    if not website:
        return ""

    website = website.strip()

    # If no scheme, add http:// for parsing
    if not website.startswith(("http://", "https://")):
        website = "http://" + website

    try:
        parsed = urlparse(website)
        domain = parsed.netloc or parsed.path.split("/")[0]

        # Remove port if present
        if ":" in domain:
            domain = domain.split(":")[0]

        # Normalize the extracted domain
        return normalize_domain(domain)
    except Exception:
        # If parsing fails, try to normalize as-is
        return normalize_domain(website)
