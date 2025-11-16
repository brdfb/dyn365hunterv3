"""Redis-based distributed caching utilities."""

import json
import hashlib
from typing import Optional, Dict, Any
from app.core.redis_client import get_redis_client, is_redis_available
from app.core.logging import logger, mask_pii

# Cache metrics tracking (in-memory counters)
_cache_metrics = {
    "hits": 0,
    "misses": 0,
    "sets": 0,
    "deletes": 0,
    "ttl_expirations": 0,
}

# Cache TTL constants (in seconds)
DNS_CACHE_TTL = 3600  # 1 hour
WHOIS_CACHE_TTL = 86400  # 24 hours
PROVIDER_CACHE_TTL = 86400  # 24 hours
SCORING_CACHE_TTL = 3600  # 1 hour
SCAN_CACHE_TTL = 3600  # 1 hour
IP_ENRICHMENT_CACHE_TTL = 86400  # 24 hours (IPs rarely change)


def _get_cache_key(prefix: str, key: str) -> str:
    """Generate cache key with prefix."""
    return f"cache:{prefix}:{key}"


def _mask_cache_key(key: str) -> str:
    """
    Mask cache key to prevent PII leakage in logs.
    
    Extracts prefix and masks the actual key part if it contains domain/PII.
    Example: "cache:dns:example.com" -> "cache:dns:<masked>"
    
    Args:
        key: Full cache key (e.g., "cache:dns:example.com")
        
    Returns:
        Masked key with PII masked (e.g., "cache:dns:<8char_hash>")
    """
    if not key:
        return ""
    
    # If key contains ":", split and mask the domain part
    if ":" in key:
        parts = key.split(":", 2)
        if len(parts) >= 3:
            # Mask the domain part (last part)
            prefix = ":".join(parts[:-1])
            domain_part = parts[-1]
            masked_domain = mask_pii(domain_part)
            return f"{prefix}:<{masked_domain}>"
        elif len(parts) == 2:
            # Mask the second part
            prefix = parts[0]
            domain_part = parts[1]
            masked_domain = mask_pii(domain_part)
            return f"{prefix}:<{masked_domain}>"
    
    # If no ":" found, mask the entire key
    return f"<{mask_pii(key)}>"


def get_cached_value(key: str) -> Optional[Any]:
    """
    Get cached value from Redis.
    
    Args:
        key: Cache key
        
    Returns:
        Cached value (deserialized from JSON) or None if not found/expired
    """
    if not is_redis_available():
        _cache_metrics["misses"] += 1
        return None
    
    redis_client = get_redis_client()
    if redis_client is None:
        _cache_metrics["misses"] += 1
        return None
    
    try:
        cached = redis_client.get(key)
        if cached:
            _cache_metrics["hits"] += 1
            return json.loads(cached.decode())
        else:
            _cache_metrics["misses"] += 1
    except Exception as e:
        # Use debug level for cache failures (common, not critical)
        # Mask key to prevent PII leakage
        logger.debug("cache_get_failed", key=_mask_cache_key(key), operation="get", error=str(e))
        _cache_metrics["misses"] += 1
    
    return None


def set_cached_value(key: str, value: Any, ttl: int) -> bool:
    """
    Set cached value in Redis with TTL.
    
    Args:
        key: Cache key
        value: Value to cache (will be serialized to JSON)
        ttl: Time to live in seconds
        
    Returns:
        True if successful, False otherwise
    """
    if not is_redis_available():
        return False
    
    redis_client = get_redis_client()
    if redis_client is None:
        return False
    
    try:
        serialized = json.dumps(value)
        redis_client.setex(key, ttl, serialized)
        _cache_metrics["sets"] += 1
        return True
    except Exception as e:
        # Use debug level for cache failures (common, not critical)
        # Mask key to prevent PII leakage
        logger.debug("cache_set_failed", key=_mask_cache_key(key), operation="set", error=str(e))
        return False


def delete_cached_value(key: str) -> bool:
    """
    Delete cached value from Redis.
    
    Args:
        key: Cache key
        
    Returns:
        True if successful, False otherwise
    """
    if not is_redis_available():
        return False
    
    redis_client = get_redis_client()
    if redis_client is None:
        return False
    
    try:
        redis_client.delete(key)
        _cache_metrics["deletes"] += 1
        return True
    except Exception as e:
        # Use debug level for cache failures (common, not critical)
        # Mask key to prevent PII leakage
        logger.debug("cache_delete_failed", key=_mask_cache_key(key), operation="delete", error=str(e))
        return False


def get_cache_metrics() -> Dict[str, Any]:
    """
    Get cache metrics (hits, misses, hit rate, etc.).
    
    Returns:
        Dictionary with cache metrics
    """
    hits = _cache_metrics["hits"]
    misses = _cache_metrics["misses"]
    total = hits + misses
    
    hit_rate = (hits / total * 100) if total > 0 else 0.0
    
    return {
        "hits": hits,
        "misses": misses,
        "total": total,
        "hit_rate_percent": round(hit_rate, 2),
        "sets": _cache_metrics["sets"],
        "deletes": _cache_metrics["deletes"],
        "ttl_expirations": _cache_metrics["ttl_expirations"],
    }


def reset_cache_metrics():
    """Reset cache metrics (for testing)."""
    global _cache_metrics
    _cache_metrics = {
        "hits": 0,
        "misses": 0,
        "sets": 0,
        "deletes": 0,
        "ttl_expirations": 0,
    }


# DNS Cache Functions
def get_cached_dns(domain: str) -> Optional[Dict[str, Any]]:
    """Get cached DNS result."""
    key = _get_cache_key("dns", domain)
    return get_cached_value(key)


def set_cached_dns(domain: str, result: Dict[str, Any]) -> bool:
    """Cache DNS result."""
    key = _get_cache_key("dns", domain)
    return set_cached_value(key, result, DNS_CACHE_TTL)


# WHOIS Cache Functions
def get_cached_whois(domain: str) -> Optional[Dict[str, Any]]:
    """Get cached WHOIS result."""
    key = _get_cache_key("whois", domain)
    return get_cached_value(key)


def set_cached_whois(domain: str, result: Optional[Dict[str, Any]]) -> bool:
    """Cache WHOIS result."""
    key = _get_cache_key("whois", domain)
    return set_cached_value(key, result, WHOIS_CACHE_TTL)


# Provider Mapping Cache Functions
def get_cached_provider(mx_root: str) -> Optional[str]:
    """Get cached provider mapping."""
    key = _get_cache_key("provider", mx_root)
    return get_cached_value(key)


def set_cached_provider(mx_root: str, provider: str) -> bool:
    """Cache provider mapping."""
    key = _get_cache_key("provider", mx_root)
    return set_cached_value(key, provider, PROVIDER_CACHE_TTL)


# Scoring Cache Functions
def _generate_signals_hash(signals: Dict[str, Any]) -> str:
    """
    Generate stable hash for signals dictionary.
    
    Args:
        signals: Signals dictionary
        
    Returns:
        16-character hex hash
    """
    # Sort keys to ensure stable hash
    sorted_signals = json.dumps(signals, sort_keys=True)
    hash_obj = hashlib.sha256(sorted_signals.encode())
    return hash_obj.hexdigest()[:16]


def get_cached_scoring(domain: str, provider: str, signals: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Get cached scoring result."""
    signals_hash = _generate_signals_hash(signals)
    key = _get_cache_key("scoring", f"{domain}:{provider}:{signals_hash}")
    return get_cached_value(key)


def set_cached_scoring(domain: str, provider: str, signals: Dict[str, Any], result: Dict[str, Any]) -> bool:
    """Cache scoring result."""
    signals_hash = _generate_signals_hash(signals)
    key = _get_cache_key("scoring", f"{domain}:{provider}:{signals_hash}")
    return set_cached_value(key, result, SCORING_CACHE_TTL)


# Full Scan Cache Functions
def get_cached_scan(domain: str) -> Optional[Dict[str, Any]]:
    """Get cached full scan result."""
    key = _get_cache_key("scan", domain)
    return get_cached_value(key)


def set_cached_scan(domain: str, result: Dict[str, Any]) -> bool:
    """Cache full scan result."""
    key = _get_cache_key("scan", domain)
    return set_cached_value(key, result, SCAN_CACHE_TTL)


def invalidate_scan_cache(domain: str) -> bool:
    """Invalidate scan cache for a domain (useful for rescan)."""
    key = _get_cache_key("scan", domain)
    return delete_cached_value(key)


# IP Enrichment Cache Functions
def get_cached_ip_enrichment(ip: str) -> Optional[Dict[str, Any]]:
    """Get cached IP enrichment result."""
    key = _get_cache_key("ip_enrichment", ip)
    return get_cached_value(key)


def set_cached_ip_enrichment(ip: str, result: Dict[str, Any]) -> bool:
    """Cache IP enrichment result."""
    key = _get_cache_key("ip_enrichment", ip)
    return set_cached_value(key, result, IP_ENRICHMENT_CACHE_TTL)

