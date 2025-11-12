"""WHOIS analysis utilities for domain signals."""
import socket
import whois
from typing import Dict, Optional, List
from datetime import datetime


# WHOIS timeout in seconds
WHOIS_TIMEOUT = 5


def get_whois_info(domain: str) -> Optional[Dict[str, any]]:
    """
    Get WHOIS information for a domain.
    
    Args:
        domain: Domain name to query
        
    Returns:
        Dictionary with WHOIS information:
        - registrar: str (registrar name) or None
        - expires_at: date (expiration date) or None
        - nameservers: List[str] (nameserver hostnames) or None
        Returns None if WHOIS lookup fails (graceful fail)
        
    Examples:
        >>> get_whois_info("example.com")
        {'registrar': 'Example Registrar', 'expires_at': date(2025, 12, 31), 'nameservers': [...]}
        >>> get_whois_info("invalid-domain-xyz-123.com")
        None
    """
    try:
        # Set socket timeout for WHOIS lookup
        socket.setdefaulttimeout(WHOIS_TIMEOUT)
        
        # Perform WHOIS lookup
        w = whois.whois(domain)
        
        # If domain doesn't exist, whois.whois() might return None or empty dict
        if not w or (isinstance(w, dict) and not w.get('domain_name')):
            return None
        
        result = {
            "registrar": None,
            "expires_at": None,
            "nameservers": None
        }
        
        # Extract registrar
        if hasattr(w, 'registrar'):
            result["registrar"] = w.registrar
        elif isinstance(w, dict) and 'registrar' in w:
            result["registrar"] = w['registrar']
        
        # Extract expiration date
        if hasattr(w, 'expiration_date'):
            exp_date = w.expiration_date
        elif isinstance(w, dict) and 'expiration_date' in w:
            exp_date = w['expiration_date']
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
                    parsed_date = datetime.strptime(exp_date, '%Y-%m-%d')
                    result["expires_at"] = parsed_date.date()
                except ValueError:
                    # Try other formats
                    try:
                        parsed_date = datetime.strptime(exp_date.split()[0], '%Y-%m-%d')
                        result["expires_at"] = parsed_date.date()
                    except ValueError:
                        pass
        
        # Extract nameservers
        if hasattr(w, 'name_servers'):
            ns = w.name_servers
        elif isinstance(w, dict) and 'name_servers' in w:
            ns = w['name_servers']
        else:
            ns = None
        
        if ns:
            # Normalize nameservers to list of strings
            if isinstance(ns, list):
                result["nameservers"] = [str(n).lower().rstrip('.') for n in ns if n]
            elif isinstance(ns, str):
                result["nameservers"] = [ns.lower().rstrip('.')]
            else:
                result["nameservers"] = []
        
        # Return None if we got no useful information
        if not result["registrar"] and not result["expires_at"] and not result["nameservers"]:
            return None
        
        return result
    
    except (socket.timeout, Exception):
        # Timeout or parsing error - graceful fail
        # Note: python-whois may raise various exceptions, catch all for graceful fail
        return None

