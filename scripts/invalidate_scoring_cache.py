#!/usr/bin/env python3
"""
Invalidate scoring cache for a specific domain or all domains.

Usage:
    python scripts/invalidate_scoring_cache.py dmkimya.com.tr
    python scripts/invalidate_scoring_cache.py --all
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.redis_client import get_redis_client, is_redis_available
from app.core.cache import invalidate_scoring_cache, invalidate_dns_cache
from app.core.logging import logger


def invalidate_scoring_cache_for_domain_manual(domain: str) -> int:
    """
    Invalidate all scoring cache entries for a specific domain.
    
    Args:
        domain: Domain name to invalidate cache for
        
    Returns:
        Number of cache keys deleted
    """
    if not is_redis_available():
        print("❌ Redis is not available")
        return 0
    
    redis_client = get_redis_client()
    if redis_client is None:
        print("❌ Could not connect to Redis")
        return 0
    
    # Pattern match for all scoring cache keys for this domain
    pattern = f"cache:scoring:{domain}:*"
    
    try:
        # Find all matching keys
        keys = list(redis_client.scan_iter(match=pattern))
        
        if not keys:
            print(f"ℹ️  No scoring cache found for domain: {domain}")
            return 0
        
        # Delete all matching keys
        deleted_count = 0
        for key in keys:
            redis_client.delete(key)
            deleted_count += 1
        
        print(f"✅ Deleted {deleted_count} scoring cache key(s) for domain: {domain}")
        return deleted_count
        
    except Exception as e:
        print(f"❌ Error invalidating cache: {e}")
        logger.error("cache_invalidation_failed", domain=domain, error=str(e))
        return 0


def invalidate_all_scoring_cache() -> int:
    """
    Invalidate all scoring cache entries.
    
    Returns:
        Number of cache keys deleted
    """
    if not is_redis_available():
        print("❌ Redis is not available")
        return 0
    
    redis_client = get_redis_client()
    if redis_client is None:
        print("❌ Could not connect to Redis")
        return 0
    
    # Pattern match for all scoring cache keys
    pattern = "cache:scoring:*"
    
    try:
        # Find all matching keys
        keys = list(redis_client.scan_iter(match=pattern))
        
        if not keys:
            print("ℹ️  No scoring cache found")
            return 0
        
        # Delete all matching keys
        deleted_count = 0
        for key in keys:
            redis_client.delete(key)
            deleted_count += 1
        
        print(f"✅ Deleted {deleted_count} scoring cache key(s)")
        return deleted_count
        
    except Exception as e:
        print(f"❌ Error invalidating cache: {e}")
        logger.error("cache_invalidation_failed", error=str(e))
        return 0


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/invalidate_scoring_cache.py <domain>")
        print("  python scripts/invalidate_scoring_cache.py --all")
        sys.exit(1)
    
    arg = sys.argv[1]
    
    if arg == "--all":
        print("🗑️  Invalidating ALL scoring cache...")
        # Use manual function for all domains
        count = invalidate_all_scoring_cache()
        if count > 0:
            print(f"✅ Successfully invalidated {count} cache key(s)")
        sys.exit(0 if count >= 0 else 1)
    else:
        domain = arg
        print(f"🗑️  Invalidating cache for domain: {domain}")
        
        # Use the cache module functions (cleaner)
        scoring_count = invalidate_scoring_cache(domain)
        dns_count = 1 if invalidate_dns_cache(domain) else 0
        
        total = scoring_count + dns_count
        if total > 0:
            print(f"✅ Successfully invalidated {scoring_count} scoring cache key(s) and {dns_count} DNS cache key(s)")
        else:
            print(f"ℹ️  No cache found for domain: {domain} (or Redis unavailable)")
        sys.exit(0)


if __name__ == "__main__":
    main()

