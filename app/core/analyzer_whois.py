"""WHOIS analysis utilities for domain signals."""

import socket
import whois
import httpx
import json
from typing import Dict, Optional, List, Tuple, Any
from datetime import datetime
from pathlib import Path
from functools import lru_cache


# WHOIS timeout in seconds
WHOIS_TIMEOUT = 5

# RDAP timeout in seconds
RDAP_TIMEOUT = 3

# Cache TTL in seconds (24 hours for WHOIS - data doesn't change)
# Note: Using Redis cache now, TTL is handled by Redis
from app.core.cache import get_cached_whois, set_cached_whois


@lru_cache(maxsize=1)
def _load_tld_config() -> Dict:
    """Load TLD server configuration."""
    current_dir = Path(__file__).parent.parent
    config_path = current_dir / "data" / "tld_whois_servers.json"

    if not config_path.exists():
        return {"tld_servers": {}, "rdap_servers": {}}

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_tld(domain: str) -> str:
    """Extract TLD from domain."""
    parts = domain.split(".")
    if len(parts) >= 2:
        return "." + parts[-1]
    return ""


def _try_rdap(domain: str) -> Optional[Dict[str, Any]]:
    """
    Try to get WHOIS info via RDAP (modern protocol).

    Args:
        domain: Domain name to query

    Returns:
        Dictionary with WHOIS information or None if fails
    """
    try:
        config = _load_tld_config()
        rdap_servers = config.get("rdap_servers", {})

        tld = _get_tld(domain)
        rdap_base = rdap_servers.get(tld)

        if not rdap_base:
            return None

        # Construct RDAP URL
        rdap_url = f"{rdap_base}{domain}"

        # Try RDAP lookup with timeout
        with httpx.Client(timeout=RDAP_TIMEOUT) as client:
            response = client.get(rdap_url, follow_redirects=True)

            if response.status_code == 200:
                data = response.json()

                result = {"registrar": None, "expires_at": None, "nameservers": None}

                # Extract registrar
                entities = data.get("entities", [])
                for entity in entities:
                    roles = entity.get("roles", [])
                    if "registrar" in roles:
                        vcards = entity.get("vcardArray", [])
                        if vcards and len(vcards) > 1:
                            # Extract organization name from vCard
                            for item in vcards[1]:
                                if isinstance(item, list) and len(item) >= 2:
                                    if item[0] == "fn" or item[0] == "org":
                                        result["registrar"] = (
                                            item[3] if len(item) > 3 else item[1]
                                        )
                                        break

                # Extract expiration date
                events = data.get("events", [])
                for event in events:
                    if event.get("eventAction") == "expiration":
                        event_date = event.get("eventDate")
                        if event_date:
                            try:
                                # Parse ISO 8601 date
                                result["expires_at"] = datetime.fromisoformat(
                                    event_date.replace("Z", "+00:00")
                                ).date()
                            except (ValueError, AttributeError):
                                pass

                # Extract nameservers
                nameservers = data.get("nameservers", [])
                if nameservers:
                    result["nameservers"] = [
                        ns.get("ldhName", "").lower().rstrip(".")
                        for ns in nameservers
                        if ns.get("ldhName")
                    ]

                # Return if we got any useful information
                if result["registrar"] or result["expires_at"] or result["nameservers"]:
                    return result

    except (httpx.TimeoutException, httpx.RequestError, Exception):
        # RDAP failed, will fallback to WHOIS
        pass

    return None


def _check_cache(domain: str) -> Optional[Dict[str, Any]]:
    """Check if domain is in Redis cache."""
    return get_cached_whois(domain)


def _set_cache(domain: str, result: Optional[Dict[str, Any]]):
    """Store result in Redis cache."""
    set_cached_whois(domain, result)


def get_whois_info(domain: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
    """
    Get WHOIS information for a domain.

    Strategy: RDAP → WHOIS fallback → graceful fail
    - Tries RDAP first (modern, faster, JSON)
    - Falls back to traditional WHOIS if RDAP fails
    - Uses TLD-specific servers when available
    - Implements Redis-based distributed caching (24 hour TTL)
    - Returns None on failure (graceful degrade)

    Args:
        domain: Domain name to query
        use_cache: Whether to use cache (default: True)

    Returns:
        Dictionary with WHOIS information:
        - registrar: str (registrar name) or None
        - expires_at: date (expiration date) or None
        - nameservers: List[str] (nameserver hostnames) or None
        Returns None if both RDAP and WHOIS fail (graceful fail)

    Examples:
        >>> get_whois_info("example.com")
        {'registrar': 'Example Registrar', 'expires_at': date(2025, 12, 31), 'nameservers': [...]}
        >>> get_whois_info("invalid-domain-xyz-123.com")
        None
    """
    # Check cache first
    if use_cache:
        cached_result = _check_cache(domain)
        if cached_result is not None:
            return cached_result

    # Try RDAP first (modern protocol, faster, JSON format)
    rdap_result = _try_rdap(domain)
    if rdap_result:
        if use_cache:
            _set_cache(domain, rdap_result)
        return rdap_result

    # Fallback to traditional WHOIS
    try:
        # Set socket timeout for WHOIS lookup
        socket.setdefaulttimeout(WHOIS_TIMEOUT)

        # Try with TLD-specific server if available
        config = _load_tld_config()
        tld_servers = config.get("tld_servers", {})
        tld = _get_tld(domain)
        whois_server = tld_servers.get(tld)

        # Perform WHOIS lookup
        if whois_server:
            # Use TLD-specific server
            w = whois.whois(domain, server=whois_server)
        else:
            # Use default WHOIS (python-whois will auto-detect)
            w = whois.whois(domain)

        # If domain doesn't exist, whois.whois() might return None or empty dict
        if not w or (isinstance(w, dict) and not w.get("domain_name")):
            return None

        result = {"registrar": None, "expires_at": None, "nameservers": None}

        # Extract registrar
        if hasattr(w, "registrar"):
            result["registrar"] = w.registrar
        elif isinstance(w, dict) and "registrar" in w:
            result["registrar"] = w["registrar"]

        # Extract expiration date
        if hasattr(w, "expiration_date"):
            exp_date = w.expiration_date
        elif isinstance(w, dict) and "expiration_date" in w:
            exp_date = w["expiration_date"]
        else:
            exp_date = None

        if exp_date:
            # Handle different date formats
            if isinstance(exp_date, list) and exp_date:
                exp_date = exp_date[0]

            if isinstance(exp_date, datetime):
                result["expires_at"] = exp_date.date()
            elif isinstance(exp_date, str):
                # Try to parse string date
                try:
                    parsed_date = datetime.strptime(exp_date, "%Y-%m-%d")
                    result["expires_at"] = parsed_date.date()
                except ValueError:
                    # Try other formats
                    try:
                        parsed_date = datetime.strptime(exp_date.split()[0], "%Y-%m-%d")
                        result["expires_at"] = parsed_date.date()
                    except ValueError:
                        pass

        # Extract nameservers
        if hasattr(w, "name_servers"):
            ns = w.name_servers
        elif isinstance(w, dict) and "name_servers" in w:
            ns = w["name_servers"]
        else:
            ns = None

        if ns:
            # Normalize nameservers to list of strings
            if isinstance(ns, list):
                result["nameservers"] = [str(n).lower().rstrip(".") for n in ns if n]
            elif isinstance(ns, str):
                result["nameservers"] = [ns.lower().rstrip(".")]
            else:
                result["nameservers"] = []

        # Return None if we got no useful information
        if (
            not result["registrar"]
            and not result["expires_at"]
            and not result["nameservers"]
        ):
            if use_cache:
                _set_cache(domain, None)
            return None

        # Cache successful result
        if use_cache:
            _set_cache(domain, result)

        return result

    except (socket.timeout, Exception):
        # Timeout or parsing error - graceful fail
        # Note: python-whois may raise various exceptions, catch all for graceful fail
        # Cache the failure to avoid repeated attempts
        if use_cache:
            _set_cache(domain, None)
        return None
