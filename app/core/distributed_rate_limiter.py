"""Distributed rate limiting using Redis with fallback to in-memory limiter."""

import time
import logging
import sentry_sdk
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.rate_limiter import RateLimiter

from app.core.redis_client import get_redis_client, is_redis_available

logger = logging.getLogger(__name__)

# Import RateLimiter locally to avoid circular import
def _get_rate_limiter_class():
    """Get RateLimiter class to avoid circular import."""
    from app.core.rate_limiter import RateLimiter
    return RateLimiter


class CircuitBreaker:
    """
    Simple circuit breaker for Redis availability.
    
    Opens circuit after consecutive failures, closes after success.
    """
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of consecutive failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.circuit_open = False
    
    def record_success(self):
        """Record successful operation and reset circuit breaker."""
        self.failure_count = 0
        self.circuit_open = False
        self.last_failure_time = None
    
    def record_failure(self):
        """Record failed operation and check if circuit should open."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.circuit_open = True
            logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures. "
                f"Will attempt recovery after {self.recovery_timeout}s"
            )
    
    def should_attempt(self) -> bool:
        """
        Check if we should attempt Redis operation.
        
        Returns:
            True if circuit is closed or recovery timeout has passed
        """
        if not self.circuit_open:
            return True
        
        if self.last_failure_time is None:
            return True
        
        elapsed = time.time() - self.last_failure_time
        if elapsed >= self.recovery_timeout:
            logger.info("Circuit breaker attempting recovery")
            self.circuit_open = False
            self.failure_count = 0
            return True
        
        return False


class DistributedRateLimiter:
    """
    Distributed rate limiter using Redis token bucket with fallback to in-memory limiter.
    
    Uses Redis for distributed rate limiting across multiple workers.
    Falls back to in-memory limiter if Redis is unavailable.
    """
    
    def __init__(
        self,
        redis_key: str,
        rate: float,
        burst: Optional[float] = None,
        fallback: Optional["RateLimiter"] = None,
    ):
        """
        Initialize distributed rate limiter.
        
        Args:
            redis_key: Redis key prefix for this limiter
            rate: Maximum requests per second
            burst: Maximum burst size (default: rate)
            fallback: In-memory rate limiter for fallback (optional, auto-created if None)
        """
        self.redis_key = redis_key
        self.rate = rate
        self.burst = burst or rate
        # Import RateLimiter locally to avoid circular import
        RateLimiter = _get_rate_limiter_class()
        self.fallback = fallback or RateLimiter(rate=rate, burst=burst)
        self.circuit_breaker = CircuitBreaker()
        
        # Redis keys
        self.tokens_key = f"rate_limit:{redis_key}:tokens"
        self.last_update_key = f"rate_limit:{redis_key}:last_update"
    
    def _acquire_redis(self, tokens: int = 1) -> Optional[bool]:
        """
        Try to acquire tokens from Redis.
        
        Args:
            tokens: Number of tokens to acquire
            
        Returns:
            True if tokens acquired, False if rate limited, None if Redis unavailable
        """
        redis_client = get_redis_client()
        if redis_client is None:
            return None
        
        try:
            now = time.time()
            
            # Use Redis pipeline for atomic operations
            pipe = redis_client.pipeline()
            
            # Get current state
            pipe.get(self.tokens_key)
            pipe.get(self.last_update_key)
            results = pipe.execute()
            
            # Parse results (Redis returns bytes, decode to float)
            current_tokens = float(results[0].decode()) if results[0] else self.burst
            last_update = float(results[1].decode()) if results[1] else now
            
            # Calculate new token count
            elapsed = now - last_update
            new_tokens = min(self.burst, current_tokens + elapsed * self.rate)
            
            # Check if we have enough tokens
            if new_tokens >= tokens:
                new_tokens -= tokens
                
                # Update Redis atomically (store as strings for compatibility)
                pipe = redis_client.pipeline()
                pipe.set(self.tokens_key, str(new_tokens))
                pipe.set(self.last_update_key, str(now))
                pipe.execute()
                
                self.circuit_breaker.record_success()
                return True
            else:
                # Update last_update even if we can't acquire tokens
                pipe = redis_client.pipeline()
                pipe.set(self.tokens_key, str(new_tokens))  # Update tokens even if not enough
                pipe.set(self.last_update_key, str(now))
                pipe.execute()
                
                self.circuit_breaker.record_success()
                return False
        
        except Exception as e:
            logger.warning(f"Redis rate limit operation failed: {str(e)}", exc_info=True)
            self.circuit_breaker.record_failure()
            return None
    
    def acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens. Returns True if successful, False if rate limited.
        
        Falls back to in-memory limiter if Redis is unavailable.
        
        Args:
            tokens: Number of tokens to acquire (default: 1)
            
        Returns:
            True if tokens acquired, False if rate limited
        """
        # Try Redis if circuit breaker allows
        if self.circuit_breaker.should_attempt() and is_redis_available():
            result = self._acquire_redis(tokens)
            if result is not None:
                return result
        
        # Fallback to in-memory limiter
        if not self.circuit_breaker.circuit_open:
            logger.warning(
                f"Rate limiter '{self.redis_key}' falling back to in-memory limiter (Redis unavailable)",
                extra={"redis_key": self.redis_key, "rate": self.rate}
            )
            # Tag Sentry event for monitoring
            sentry_sdk.set_tag("rate_limiter_fallback", self.redis_key)
            sentry_sdk.set_context("rate_limiter", {
                "redis_key": self.redis_key,
                "rate": self.rate,
                "fallback_mode": True
            })
        
        return self.fallback.acquire(tokens)
    
    def wait(self, tokens: int = 1) -> float:
        """
        Wait until tokens are available. Returns wait time in seconds.
        
        Falls back to in-memory limiter if Redis is unavailable.
        
        Args:
            tokens: Number of tokens to acquire (default: 1)
            
        Returns:
            Wait time in seconds
        """
        # Try Redis if circuit breaker allows
        if self.circuit_breaker.should_attempt() and is_redis_available():
            result = self._acquire_redis(tokens)
            if result is not None:
                if result:
                    return 0.0
                else:
                    # Calculate wait time based on rate
                    # This is approximate - for exact wait time, we'd need to check Redis again
                    return tokens / self.rate
        
        # Fallback to in-memory limiter
        if not self.circuit_breaker.circuit_open:
            logger.warning(
                f"Rate limiter '{self.redis_key}' falling back to in-memory limiter (Redis unavailable)",
                extra={"redis_key": self.redis_key, "rate": self.rate}
            )
            # Tag Sentry event for monitoring
            sentry_sdk.set_tag("rate_limiter_fallback", self.redis_key)
            sentry_sdk.set_context("rate_limiter", {
                "redis_key": self.redis_key,
                "rate": self.rate,
                "fallback_mode": True
            })
        
        return self.fallback.wait(tokens)

