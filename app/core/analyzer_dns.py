"""DNS analysis utilities for domain signals."""
import socket
import dns.resolver
import dns.exception
from typing import Dict, Optional, List
from urllib.parse import urlparse


# DNS timeout in seconds
DNS_TIMEOUT = 10

# Public DNS servers as fallback
PUBLIC_DNS_SERVERS = ['8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1']


def _get_resolver():
    """
    Get DNS resolver with proper configuration.
    
    Uses public DNS servers for reliable resolution in containers.
    """
    resolver = dns.resolver.Resolver()
    resolver.timeout = DNS_TIMEOUT
    resolver.lifetime = DNS_TIMEOUT
    
    # Use public DNS servers for reliable resolution in containers
    # This ensures DNS works even if container DNS is misconfigured
    resolver.nameservers = PUBLIC_DNS_SERVERS
    
    return resolver


def get_mx_records(domain: str) -> List[str]:
    """
    Get MX records for a domain.
    
    Args:
        domain: Domain name to query
        
    Returns:
        List of MX record hostnames (sorted by priority, lowest first)
        Returns empty list if no MX records found or on error
        
    Examples:
        >>> get_mx_records("google.com")
        ['aspmx.l.google.com', 'alt1.aspmx.l.google.com', ...]
    """
    try:
        resolver = _get_resolver()
        mx_records = resolver.resolve(domain, 'MX')
        
        # Sort by priority (lower is better)
        mx_list = []
        for mx in mx_records:
            mx_list.append((mx.preference, str(mx.exchange).rstrip('.')))
        
        mx_list.sort(key=lambda x: x[0])
        
        # Return just the hostnames
        return [mx[1] for mx in mx_list]
    
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
        # No MX records found
        return []
    except (dns.exception.Timeout, socket.timeout):
        # Timeout
        return []
    except Exception:
        # Any other error
        return []


def extract_mx_root(mx_hostname: str) -> Optional[str]:
    """
    Extract root domain from MX hostname.
    
    Handles two-part TLDs like .com.tr, .co.uk, .com.au, etc.
    
    Examples:
        >>> extract_mx_root("outlook-com.olc.protection.outlook.com")
        'outlook.com'
        >>> extract_mx_root("aspmx.l.google.com")
        'google.com'
        >>> extract_mx_root("mail.example.com")
        'example.com'
        >>> extract_mx_root("aspmx.vit.com.tr")
        'vit.com.tr'
        >>> extract_mx_root("mail.example.co.uk")
        'example.co.uk'
    """
    if not mx_hostname:
        return None
    
    # Remove trailing dot
    mx_hostname = mx_hostname.rstrip('.')
    
    # Split by dots
    parts = mx_hostname.split('.')
    
    if len(parts) < 2:
        return mx_hostname
    
    # Common two-part TLDs (country code + generic)
    # These require taking the last 3 parts instead of 2
    two_part_tlds = [
        'com.tr', 'net.tr', 'org.tr', 'gov.tr', 'edu.tr',  # Turkey
        'co.uk', 'org.uk', 'ac.uk', 'gov.uk',  # UK
        'com.au', 'net.au', 'org.au', 'gov.au', 'edu.au',  # Australia
        'co.za', 'org.za', 'gov.za',  # South Africa
        'com.br', 'net.br', 'org.br', 'gov.br',  # Brazil
        'co.jp', 'ne.jp', 'or.jp', 'go.jp', 'ac.jp',  # Japan
        'com.cn', 'net.cn', 'org.cn', 'gov.cn', 'edu.cn',  # China
        'co.in', 'net.in', 'org.in', 'gov.in', 'edu.in',  # India
        'com.mx', 'net.mx', 'org.mx', 'gov.mx',  # Mexico
        'com.ar', 'net.ar', 'org.ar', 'gov.ar',  # Argentina
        'co.nz', 'net.nz', 'org.nz', 'govt.nz',  # New Zealand
        'com.sg', 'net.sg', 'org.sg', 'gov.sg',  # Singapore
        'com.my', 'net.my', 'org.my', 'gov.my',  # Malaysia
        'com.ph', 'net.ph', 'org.ph', 'gov.ph',  # Philippines
    ]
    
    # Check if the last 2 parts form a two-part TLD
    last_two = '.'.join(parts[-2:]).lower()
    if last_two in two_part_tlds:
        # For two-part TLDs, take the last 3 parts
        if len(parts) >= 3:
            return '.'.join(parts[-3:])
        else:
            return mx_hostname
    
    # For standard TLDs, take the last 2 parts
    return '.'.join(parts[-2:])


def check_spf(domain: str) -> bool:
    """
    Check if domain has SPF record.
    
    Args:
        domain: Domain name to check
        
    Returns:
        True if SPF record exists, False otherwise
    """
    try:
        resolver = _get_resolver()
        txt_records = resolver.resolve(domain, 'TXT')
        
        for txt in txt_records:
            txt_string = ''.join([s.decode('utf-8') if isinstance(s, bytes) else str(s) for s in txt.strings])
            if txt_string.startswith('v=spf1'):
                return True
        
        return False
    
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
        return False
    except (dns.exception.Timeout, socket.timeout):
        return False
    except Exception:
        return False


def check_dkim(domain: str, selector: str = "default") -> bool:
    """
    Check if domain has DKIM record.
    
    Args:
        domain: Domain name to check
        selector: DKIM selector (default: "default")
        
    Returns:
        True if DKIM record exists, False otherwise
    """
    try:
        resolver = _get_resolver()
        dkim_domain = f"{selector}._domainkey.{domain}"
        txt_records = resolver.resolve(dkim_domain, 'TXT')
        
        for txt in txt_records:
            txt_string = ''.join([s.decode('utf-8') if isinstance(s, bytes) else str(s) for s in txt.strings])
            if 'v=DKIM1' in txt_string or 'k=rsa' in txt_string:
                return True
        
        return False
    
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
        # Try alternative selectors
        common_selectors = ["default", "google", "selector1", "selector2"]
        for alt_selector in common_selectors:
            if alt_selector == selector:
                continue
            try:
                resolver = _get_resolver()
                dkim_domain = f"{alt_selector}._domainkey.{domain}"
                txt_records = resolver.resolve(dkim_domain, 'TXT')
                for txt in txt_records:
                    txt_string = ''.join([s.decode('utf-8') if isinstance(s, bytes) else str(s) for s in txt.strings])
                    if 'v=DKIM1' in txt_string or 'k=rsa' in txt_string:
                        return True
            except Exception:
                continue
        return False
    except (dns.exception.Timeout, socket.timeout):
        return False
    except Exception:
        return False


def check_dmarc(domain: str) -> Optional[str]:
    """
    Check DMARC policy for a domain.
    
    Args:
        domain: Domain name to check
        
    Returns:
        DMARC policy string: "none", "quarantine", "reject", or None if not found
    """
    try:
        resolver = _get_resolver()
        dmarc_domain = f"_dmarc.{domain}"
        txt_records = resolver.resolve(dmarc_domain, 'TXT')
        
        for txt in txt_records:
            txt_string = ''.join([s.decode('utf-8') if isinstance(s, bytes) else str(s) for s in txt.strings])
            if 'v=DMARC1' in txt_string:
                # Parse policy
                if 'p=none' in txt_string or 'p=NONE' in txt_string:
                    return "none"
                elif 'p=quarantine' in txt_string or 'p=QUARANTINE' in txt_string:
                    return "quarantine"
                elif 'p=reject' in txt_string or 'p=REJECT' in txt_string:
                    return "reject"
                else:
                    # Default to "none" if policy not explicitly set
                    return "none"
        
        return None
    
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
        return None
    except (dns.exception.Timeout, socket.timeout):
        return None
    except Exception:
        return None


def analyze_dns(domain: str) -> Dict[str, any]:
    """
    Perform complete DNS analysis for a domain.
    
    Analyzes:
    - MX records (and extracts root domain)
    - SPF record
    - DKIM record
    - DMARC policy
    
    Args:
        domain: Domain name to analyze
        
    Returns:
        Dictionary with analysis results:
        - mx_records: List of MX hostnames
        - mx_root: Root domain of first MX record (or None)
        - spf: bool (SPF record exists)
        - dkim: bool (DKIM record exists)
        - dmarc_policy: str ("none", "quarantine", "reject", or None)
        - status: str ("success", "dns_timeout", "invalid_domain")
    """
    result = {
        "mx_records": [],
        "mx_root": None,
        "spf": False,
        "dkim": False,
        "dmarc_policy": None,
        "status": "success"
    }
    
    try:
        # Get MX records
        mx_records = get_mx_records(domain)
        result["mx_records"] = mx_records
        
        # Extract MX root from first MX record
        if mx_records:
            result["mx_root"] = extract_mx_root(mx_records[0])
        
        # Check SPF
        result["spf"] = check_spf(domain)
        
        # Check DKIM
        result["dkim"] = check_dkim(domain)
        
        # Check DMARC
        result["dmarc_policy"] = check_dmarc(domain)
        
    except (dns.exception.Timeout, socket.timeout):
        result["status"] = "dns_timeout"
    except Exception as e:
        result["status"] = "invalid_domain"
    
    return result

