"""Redis-based distributed caching utilities."""

import json
import hashlib
import logging
from typing import Optional, Dict, Any
from app.core.redis_client import get_redis_client, is_redis_available

logger = logging.getLogger(__name__)

# Cache TTL constants (in seconds)
DNS_CACHE_TTL = 3600  # 1 hour
WHOIS_CACHE_TTL = 86400  # 24 hours
PROVIDER_CACHE_TTL = 86400  # 24 hours
SCORING_CACHE_TTL = 3600  # 1 hour
SCAN_CACHE_TTL = 3600  # 1 hour


def _get_cache_key(prefix: str, key: str) -> str:
    """Generate cache key with prefix."""
    return f"cache:{prefix}:{key}"


def get_cached_value(key: str) -> Optional[Any]:
    """
    Get cached value from Redis.
    
    Args:
        key: Cache key
        
    Returns:
        Cached value (deserialized from JSON) or None if not found/expired
    """
    if not is_redis_available():
        return None
    
    redis_client = get_redis_client()
    if redis_client is None:
        return None
    
    try:
        cached = redis_client.get(key)
        if cached:
            return json.loads(cached.decode())
    except Exception as e:
        logger.warning(f"Cache get failed for key {key}: {str(e)}")
    
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
        return True
    except Exception as e:
        logger.warning(f"Cache set failed for key {key}: {str(e)}")
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
        return True
    except Exception as e:
        logger.warning(f"Cache delete failed for key {key}: {str(e)}")
        return False


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

