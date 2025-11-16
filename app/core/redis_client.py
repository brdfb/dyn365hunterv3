"""Redis client wrapper with connection pooling and circuit breaker support."""

import redis
from typing import Optional
from app.config import settings
from app.core.logging import logger

# Global Redis connection pool
_redis_pool: Optional[redis.ConnectionPool] = None
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> Optional[redis.Redis]:
    """
    Get Redis client with connection pooling.
    
    Returns:
        Redis client instance, or None if Redis is unavailable
    """
    global _redis_pool, _redis_client
    
    if _redis_client is not None:
        return _redis_client
    
    try:
        # Create connection pool for better performance
        _redis_pool = redis.ConnectionPool.from_url(
            settings.redis_url,
            decode_responses=False,  # Keep binary for rate limiting operations
            max_connections=50,
            retry_on_timeout=True,
        )
        _redis_client = redis.Redis(connection_pool=_redis_pool)
        
        # Test connection
        _redis_client.ping()
        logger.info("redis_client_initialized")
        return _redis_client
    except Exception as e:
        # Use error level for Redis initialization failure (critical infrastructure)
        logger.error("redis_client_initialization_failed", error=str(e), reason="connection_failed")
        _redis_pool = None
        _redis_client = None
        return None


def is_redis_available() -> bool:
    """
    Check if Redis is available.
    
    Returns:
        True if Redis is available, False otherwise
    """
    client = get_redis_client()
    if client is None:
        return False
    
    try:
        client.ping()
        return True
    except Exception:
        return False


def reset_redis_client():
    """Reset Redis client (for testing or reconnection)."""
    global _redis_pool, _redis_client
    
    if _redis_client is not None:
        try:
            _redis_client.close()
        except Exception:
            pass
    
    _redis_pool = None
    _redis_client = None

