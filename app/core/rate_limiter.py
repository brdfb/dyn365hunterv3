"""Rate limiting utilities for DNS and WHOIS queries."""
import time
import asyncio
from typing import Dict, Optional
from collections import defaultdict
from threading import Lock


class RateLimiter:
    """
    Thread-safe rate limiter using token bucket algorithm.
    
    Args:
        rate: Maximum requests per second
        burst: Maximum burst size (default: rate)
    """
    
    def __init__(self, rate: float, burst: Optional[float] = None):
        self.rate = rate
        self.burst = burst or rate
        self.tokens = self.burst
        self.last_update = time.time()
        self.lock = Lock()
    
    def acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens. Returns True if successful, False if rate limited.
        
        Args:
            tokens: Number of tokens to acquire (default: 1)
            
        Returns:
            True if tokens acquired, False if rate limited
        """
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            
            # Add tokens based on elapsed time
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            # Check if we have enough tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def wait(self, tokens: int = 1) -> float:
        """
        Wait until tokens are available. Returns wait time in seconds.
        
        Args:
            tokens: Number of tokens to acquire (default: 1)
            
        Returns:
            Wait time in seconds
        """
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            
            # Add tokens based on elapsed time
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            # Calculate wait time if not enough tokens
            if self.tokens < tokens:
                wait_time = (tokens - self.tokens) / self.rate
                self.tokens = 0
                return wait_time
            else:
                self.tokens -= tokens
                return 0.0


# Global rate limiters (shared across workers)
# DNS: 10 requests/second per worker
# WHOIS: 5 requests/second per worker
_dns_rate_limiter: Optional[RateLimiter] = None
_whois_rate_limiter: Optional[RateLimiter] = None
_rate_limiter_lock = Lock()


def get_dns_rate_limiter() -> RateLimiter:
    """Get DNS rate limiter (10 req/s)."""
    global _dns_rate_limiter
    with _rate_limiter_lock:
        if _dns_rate_limiter is None:
            _dns_rate_limiter = RateLimiter(rate=10.0, burst=10.0)
        return _dns_rate_limiter


def get_whois_rate_limiter() -> RateLimiter:
    """Get WHOIS rate limiter (5 req/s)."""
    global _whois_rate_limiter
    with _rate_limiter_lock:
        if _whois_rate_limiter is None:
            _whois_rate_limiter = RateLimiter(rate=5.0, burst=5.0)
        return _whois_rate_limiter


def wait_for_dns_rate_limit():
    """Wait for DNS rate limit (10 req/s)."""
    limiter = get_dns_rate_limiter()
    wait_time = limiter.wait()
    if wait_time > 0:
        time.sleep(wait_time)


def wait_for_whois_rate_limit():
    """Wait for WHOIS rate limit (5 req/s)."""
    limiter = get_whois_rate_limiter()
    wait_time = limiter.wait()
    if wait_time > 0:
        time.sleep(wait_time)

