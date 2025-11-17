"""DNS analysis utilities for domain signals."""

import socket
import re
import dns.resolver
import dns.exception
from typing import Dict, Optional, List, Any
from urllib.parse import urlparse
from app.core.cache import get_cached_dns, set_cached_dns


# DNS timeout in seconds
DNS_TIMEOUT = 10

# Public DNS servers as fallback
PUBLIC_DNS_SERVERS = ["8.8.8.8", "8.8.4.4", "1.1.1.1", "1.0.0.1"]


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
        mx_records = resolver.resolve(domain, "MX")

        # Sort by priority (lower is better)
        mx_list = []
        for mx in mx_records:
            mx_list.append((mx.preference, str(mx.exchange).rstrip(".")))

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


def resolve_hostname_to_ip(hostname: str) -> Optional[str]:
    """
    Resolve hostname to IPv4 address.
    
    Args:
        hostname: Hostname to resolve
        
    Returns:
        First IPv4 address found, or None on error
        
    Examples:
        >>> resolve_hostname_to_ip("google.com")
        '142.250.185.14'
    """
    try:
        resolver = _get_resolver()
        a_records = resolver.resolve(hostname, "A")
        if a_records:
            return str(a_records[0])
    except Exception:
        pass
    return None


def resolve_domain_ip_candidates(domain: str, mx_hosts: List[str]) -> List[str]:
    """
    Resolve domain and MX hostnames to IP addresses.
    
    Collects IP addresses from:
    1. MX record hostnames (all MX records)
    2. Root domain A record
    
    Args:
        domain: Root domain name
        mx_hosts: List of MX hostnames
        
    Returns:
        List of unique IP addresses (may be empty)
        
    Examples:
        >>> resolve_domain_ip_candidates("example.com", ["mail.example.com"])
        ['192.0.2.1', '192.0.2.2']
    """
    ips = []
    
    # 1) MX host IPs
    for mx in mx_hosts:
        ip = resolve_hostname_to_ip(mx)
        if ip and ip not in ips:
            ips.append(ip)
    
    # 2) Root domain IP
    root_ip = resolve_hostname_to_ip(domain)
    if root_ip and root_ip not in ips:
        ips.append(root_ip)
    
    return ips


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
    mx_hostname = mx_hostname.rstrip(".")

    # Split by dots
    parts = mx_hostname.split(".")

    if len(parts) < 2:
        return mx_hostname

    # Common two-part TLDs (country code + generic)
    # These require taking the last 3 parts instead of 2
    two_part_tlds = [
        "com.tr",
        "net.tr",
        "org.tr",
        "gov.tr",
        "edu.tr",  # Turkey
        "co.uk",
        "org.uk",
        "ac.uk",
        "gov.uk",  # UK
        "com.au",
        "net.au",
        "org.au",
        "gov.au",
        "edu.au",  # Australia
        "co.za",
        "org.za",
        "gov.za",  # South Africa
        "com.br",
        "net.br",
        "org.br",
        "gov.br",  # Brazil
        "co.jp",
        "ne.jp",
        "or.jp",
        "go.jp",
        "ac.jp",  # Japan
        "com.cn",
        "net.cn",
        "org.cn",
        "gov.cn",
        "edu.cn",  # China
        "co.in",
        "net.in",
        "org.in",
        "gov.in",
        "edu.in",  # India
        "com.mx",
        "net.mx",
        "org.mx",
        "gov.mx",  # Mexico
        "com.ar",
        "net.ar",
        "org.ar",
        "gov.ar",  # Argentina
        "co.nz",
        "net.nz",
        "org.nz",
        "govt.nz",  # New Zealand
        "com.sg",
        "net.sg",
        "org.sg",
        "gov.sg",  # Singapore
        "com.my",
        "net.my",
        "org.my",
        "gov.my",  # Malaysia
        "com.ph",
        "net.ph",
        "org.ph",
        "gov.ph",  # Philippines
    ]

    # Check if the last 2 parts form a two-part TLD
    last_two = ".".join(parts[-2:]).lower()
    if last_two in two_part_tlds:
        # For two-part TLDs, take the last 3 parts
        if len(parts) >= 3:
            return ".".join(parts[-3:])
        else:
            return mx_hostname

    # For standard TLDs, take the last 2 parts
    return ".".join(parts[-2:])


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
        txt_records = resolver.resolve(domain, "TXT")

        for txt in txt_records:
            txt_string = "".join(
                [
                    s.decode("utf-8") if isinstance(s, bytes) else str(s)
                    for s in txt.strings
                ]
            )
            if txt_string.startswith("v=spf1"):
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
        txt_records = resolver.resolve(dkim_domain, "TXT")

        for txt in txt_records:
            txt_string = "".join(
                [
                    s.decode("utf-8") if isinstance(s, bytes) else str(s)
                    for s in txt.strings
                ]
            )
            if "v=DKIM1" in txt_string or "k=rsa" in txt_string:
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
                txt_records = resolver.resolve(dkim_domain, "TXT")
                for txt in txt_records:
                    txt_string = "".join(
                        [
                            s.decode("utf-8") if isinstance(s, bytes) else str(s)
                            for s in txt.strings
                        ]
                    )
                    if "v=DKIM1" in txt_string or "k=rsa" in txt_string:
                        return True
            except Exception:
                continue
        return False
    except (dns.exception.Timeout, socket.timeout):
        return False
    except Exception:
        return False


def check_dmarc(domain: str) -> Dict[str, Any]:
    """
    Check DMARC policy and coverage for a domain.

    Args:
        domain: Domain name to check

    Returns:
        Dictionary with:
        - policy: "none", "quarantine", "reject", or None if not found
        - coverage: Integer 0-100 if DMARC record found (default: 100 if pct= not specified), None if DMARC record not found
        - record: Full DMARC record string (for reference)
    """
    result = {
        "policy": None,
        "coverage": None,  # DMARC record yoksa coverage None olmalı
        "record": None,
    }
    
    try:
        resolver = _get_resolver()
        dmarc_domain = f"_dmarc.{domain}"
        txt_records = resolver.resolve(dmarc_domain, "TXT")

        for txt in txt_records:
            txt_string = "".join(
                [
                    s.decode("utf-8") if isinstance(s, bytes) else str(s)
                    for s in txt.strings
                ]
            )
            if "v=DMARC1" in txt_string:
                result["record"] = txt_string
                
                # Parse policy
                if "p=none" in txt_string or "p=NONE" in txt_string:
                    result["policy"] = "none"
                elif "p=quarantine" in txt_string or "p=QUARANTINE" in txt_string:
                    result["policy"] = "quarantine"
                elif "p=reject" in txt_string or "p=REJECT" in txt_string:
                    result["policy"] = "reject"
                else:
                    # Default to "none" if policy not explicitly set
                    result["policy"] = "none"
                
                # Parse coverage (pct=)
                # DMARC spec: pct=0-100 (default: 100 if not specified)
                pct_match = re.search(r'pct=(\d+)', txt_string, re.IGNORECASE)
                if pct_match:
                    coverage = int(pct_match.group(1))
                    # Ensure coverage is in valid range (0-100)
                    result["coverage"] = max(0, min(100, coverage))
                else:
                    # DMARC record var ama pct= belirtilmemiş → DMARC spec default: 100
                    result["coverage"] = 100
                
                return result

        # DMARC record bulunamadı → policy ve coverage None kalır
        return result

    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
        # DMARC record yok → policy ve coverage None kalır
        return result
    except (dns.exception.Timeout, socket.timeout):
        # Timeout → policy ve coverage None kalır
        return result
    except Exception:
        # Hata → policy ve coverage None kalır
        return result


def analyze_dns(domain: str, use_cache: bool = True) -> Dict[str, Any]:
    """
    Perform complete DNS analysis for a domain.

    Analyzes:
    - MX records (and extracts root domain)
    - SPF record
    - DKIM record
    - DMARC policy and coverage

    Uses Redis-based caching (1 hour TTL) to reduce DNS queries.

    Args:
        domain: Domain name to analyze
        use_cache: Whether to use cache (default: True)

    Returns:
        Dictionary with analysis results:
        - mx_records: List of MX hostnames
        - mx_root: Root domain of first MX record (or None)
        - spf: bool (SPF record exists)
        - dkim: bool (DKIM record exists)
        - dmarc_policy: str ("none", "quarantine", "reject", or None)
        - dmarc_coverage: int (0-100 if DMARC record found, None if not found)
        - dmarc_record: str (Full DMARC record string, or None)
        - status: str ("success", "dns_timeout", "invalid_domain")
    """
    # Check cache first
    if use_cache:
        cached_result = get_cached_dns(domain)
        if cached_result is not None:
            return cached_result

    result = {
        "mx_records": [],
        "mx_root": None,
        "spf": False,
        "dkim": False,
        "dmarc_policy": None,
        "dmarc_coverage": None,  # None if DMARC record not found
        "dmarc_record": None,
        "status": "success",
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

        # Check DMARC (returns dict with policy, coverage, record)
        dmarc_result = check_dmarc(domain)
        result["dmarc_policy"] = dmarc_result.get("policy")
        result["dmarc_coverage"] = dmarc_result.get("coverage")  # None if DMARC record not found
        result["dmarc_record"] = dmarc_result.get("record")

    except (dns.exception.Timeout, socket.timeout):
        result["status"] = "dns_timeout"
    except Exception as e:
        result["status"] = "invalid_domain"

    # Cache result (even if failed, to avoid repeated queries)
    if use_cache:
        set_cached_dns(domain, result)

    return result
