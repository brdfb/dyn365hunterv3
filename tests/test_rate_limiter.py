"""Unit tests for rate limiting functionality."""

import pytest
import time
from app.core.rate_limiter import (
    RateLimiter,
    wait_for_dns_rate_limit,
    wait_for_whois_rate_limit,
)


class TestRateLimiter:
    """Test rate limiter functionality."""

    def test_rate_limiter_acquire_success(self):
        """Test successful token acquisition."""
        limiter = RateLimiter(rate=10.0, burst=10.0)

        # Should succeed immediately
        assert limiter.acquire() is True
        assert limiter.tokens == 9.0

    def test_rate_limiter_acquire_failure(self):
        """Test rate limiting when tokens exhausted."""
        limiter = RateLimiter(rate=1.0, burst=1.0)

        # First acquire should succeed
        assert limiter.acquire() is True

        # Second acquire should fail (no tokens)
        assert limiter.acquire() is False

    def test_rate_limiter_token_refill(self):
        """Test token refill over time."""
        limiter = RateLimiter(rate=10.0, burst=10.0)

        # Exhaust tokens
        for _ in range(10):
            limiter.acquire()

        assert limiter.tokens == 0.0

        # Wait 0.1 seconds (should refill 1 token)
        time.sleep(0.11)
        assert limiter.acquire() is True

    def test_rate_limiter_wait(self):
        """Test wait functionality."""
        limiter = RateLimiter(rate=10.0, burst=10.0)

        # Exhaust tokens
        for _ in range(10):
            limiter.acquire()

        # Wait should return time needed
        wait_time = limiter.wait()
        assert wait_time > 0
        assert wait_time <= 0.2  # Should be around 0.1s for 1 token at 10 req/s

    def test_rate_limiter_burst_limit(self):
        """Test burst limit."""
        limiter = RateLimiter(rate=10.0, burst=5.0)

        # Should only allow burst amount
        for _ in range(5):
            assert limiter.acquire() is True

        # Should fail after burst
        assert limiter.acquire() is False

        # Tokens should not exceed burst
        assert limiter.tokens == 0.0


class TestDNSRateLimiter:
    """Test DNS rate limiter (10 req/s)."""

    def test_dns_rate_limiter_initial(self):
        """Test DNS rate limiter initial state."""
        from app.core.rate_limiter import get_dns_rate_limiter

        limiter = get_dns_rate_limiter()
        assert limiter.rate == 10.0
        assert limiter.burst == 10.0

    def test_dns_rate_limiter_wait(self):
        """Test DNS rate limiter wait function."""
        # This is a functional test - actual wait time depends on system
        start = time.time()
        wait_for_dns_rate_limit()
        elapsed = time.time() - start

        # Should be very fast (no wait needed initially)
        assert elapsed < 0.1


class TestWHOISRateLimiter:
    """Test WHOIS rate limiter (5 req/s)."""

    def test_whois_rate_limiter_initial(self):
        """Test WHOIS rate limiter initial state."""
        from app.core.rate_limiter import get_whois_rate_limiter

        limiter = get_whois_rate_limiter()
        assert limiter.rate == 5.0
        assert limiter.burst == 5.0

    def test_whois_rate_limiter_wait(self):
        """Test WHOIS rate limiter wait function."""
        # This is a functional test - actual wait time depends on system
        start = time.time()
        wait_for_whois_rate_limit()
        elapsed = time.time() - start

        # Should be very fast (no wait needed initially)
        assert elapsed < 0.1
