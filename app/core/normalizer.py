"""Domain normalization utilities."""
import re
from urllib.parse import urlparse
from idna import decode as idna_decode, encode as idna_encode


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
    
    # Remove trailing dots
    domain = domain.rstrip('.')
    
    # Convert to lowercase
    domain = domain.lower()
    
    # Remove www. prefix (case-insensitive)
    if domain.startswith('www.'):
        domain = domain[4:]
    
    # Decode punycode if present
    try:
        if domain.startswith('xn--'):
            domain = idna_decode(domain.encode('ascii')).decode('utf-8')
    except (UnicodeDecodeError, UnicodeError):
        # If punycode decode fails, keep original
        pass
    
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
    if '@' not in email:
        return ""
    
    # Extract domain part
    parts = email.rsplit('@', 1)
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
    if not website.startswith(('http://', 'https://')):
        website = 'http://' + website
    
    try:
        parsed = urlparse(website)
        domain = parsed.netloc or parsed.path.split('/')[0]
        
        # Remove port if present
        if ':' in domain:
            domain = domain.split(':')[0]
        
        # Normalize the extracted domain
        return normalize_domain(domain)
    except Exception:
        # If parsing fails, try to normalize as-is
        return normalize_domain(website)

