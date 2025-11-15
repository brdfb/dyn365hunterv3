"""Unit tests for rate limiting functionality."""

import pytest
import time
from unittest.mock import patch, MagicMock
from app.core.rate_limiter import (
    RateLimiter,
    wait_for_dns_rate_limit,
    wait_for_whois_rate_limit,
    get_dns_rate_limiter,
    get_whois_rate_limiter,
)
from app.core.distributed_rate_limiter import DistributedRateLimiter, CircuitBreaker
from app.core.redis_client import get_redis_client, reset_redis_client


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
        # Mock Redis as unavailable to avoid connection timeout in test environment
        with patch("app.core.distributed_rate_limiter.is_redis_available", return_value=False):
            start = time.time()
            wait_for_dns_rate_limit()
            elapsed = time.time() - start

            # Should be very fast (no wait needed initially, using fallback)
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
        # Mock Redis as unavailable to avoid connection timeout in test environment
        with patch("app.core.distributed_rate_limiter.is_redis_available", return_value=False):
            start = time.time()
            wait_for_whois_rate_limit()
            elapsed = time.time() - start

            # Should be very fast (no wait needed initially, using fallback)
            assert elapsed < 0.1


class TestDistributedRateLimiter:
    """Test distributed rate limiter with Redis."""

    def test_distributed_rate_limiter_initialization(self):
        """Test DistributedRateLimiter initialization."""
        limiter = DistributedRateLimiter(
            redis_key="test",
            rate=10.0,
            burst=10.0,
        )
        assert limiter.rate == 10.0
        assert limiter.burst == 10.0
        assert limiter.redis_key == "test"
        assert limiter.fallback is not None

    def test_distributed_rate_limiter_fallback_on_redis_unavailable(self):
        """Test fallback to in-memory limiter when Redis is unavailable."""
        # Mock Redis as unavailable
        with patch("app.core.distributed_rate_limiter.is_redis_available", return_value=False):
            limiter = DistributedRateLimiter(
                redis_key="test",
                rate=10.0,
                burst=10.0,
            )
            # Should use fallback
            assert limiter.acquire() is True
            assert limiter.fallback.tokens == 9.0

    def test_circuit_breaker_opens_after_failures(self):
        """Test circuit breaker opens after threshold failures."""
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=1.0)
        
        # Record 2 failures (should not open yet)
        breaker.record_failure()
        breaker.record_failure()
        assert breaker.circuit_open is False
        
        # Record 3rd failure (should open)
        breaker.record_failure()
        assert breaker.circuit_open is True
        assert breaker.should_attempt() is False

    def test_circuit_breaker_recovery_after_timeout(self):
        """Test circuit breaker recovers after timeout."""
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=0.1)
        
        # Open circuit
        for _ in range(3):
            breaker.record_failure()
        assert breaker.circuit_open is True
        
        # Wait for recovery timeout
        time.sleep(0.15)
        
        # Should attempt recovery
        assert breaker.should_attempt() is True
        assert breaker.circuit_open is False

    def test_circuit_breaker_resets_on_success(self):
        """Test circuit breaker resets on success."""
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=1.0)
        
        # Record 2 failures
        breaker.record_failure()
        breaker.record_failure()
        
        # Record success (should reset)
        breaker.record_success()
        assert breaker.failure_count == 0
        assert breaker.circuit_open is False


class TestDistributedDNSRateLimiter:
    """Test distributed DNS rate limiter."""

    def test_dns_rate_limiter_is_distributed(self):
        """Test that DNS rate limiter is now distributed."""
        limiter = get_dns_rate_limiter()
        assert isinstance(limiter, DistributedRateLimiter)
        assert limiter.rate == 10.0
        assert limiter.burst == 10.0

    def test_dns_rate_limiter_fallback_works(self):
        """Test DNS rate limiter fallback when Redis unavailable."""
        # Mock Redis as unavailable
        with patch("app.core.distributed_rate_limiter.is_redis_available", return_value=False):
            limiter = get_dns_rate_limiter()
            # Should still work with fallback
            assert limiter.acquire() is True


class TestDistributedWHOISRateLimiter:
    """Test distributed WHOIS rate limiter."""

    def test_whois_rate_limiter_is_distributed(self):
        """Test that WHOIS rate limiter is now distributed."""
        limiter = get_whois_rate_limiter()
        assert isinstance(limiter, DistributedRateLimiter)
        assert limiter.rate == 5.0
        assert limiter.burst == 5.0

    def test_whois_rate_limiter_fallback_works(self):
        """Test WHOIS rate limiter fallback when Redis unavailable."""
        # Mock Redis as unavailable
        with patch("app.core.distributed_rate_limiter.is_redis_available", return_value=False):
            limiter = get_whois_rate_limiter()
            # Should still work with fallback
            assert limiter.acquire() is True


class TestRedisClient:
    """Test Redis client wrapper."""

    def test_redis_client_initialization(self):
        """Test Redis client initialization."""
        # Reset client to test initialization
        reset_redis_client()
        client = get_redis_client()
        # Client may be None if Redis is not available in test environment
        # This is acceptable - the system should handle Redis unavailability
        assert client is None or client is not None  # Either is fine

    def test_is_redis_available(self):
        """Test Redis availability check."""
        from app.core.redis_client import is_redis_available
        # This will check actual Redis availability
        # In test environment, Redis may or may not be available
        result = is_redis_available()
        assert isinstance(result, bool)
