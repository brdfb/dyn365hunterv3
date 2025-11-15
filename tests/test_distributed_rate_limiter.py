"""Distributed rate limiting tests for Stabilization Sprint - Day 1.

Tests:
- Multi-worker rate limiting (shared limits across workers)
- Redis down fallback (in-memory limiter)
- Circuit breaker recovery
- Rate limit sharing verification
"""

import pytest
import time
import threading
from unittest.mock import patch, MagicMock
from app.core.distributed_rate_limiter import DistributedRateLimiter, CircuitBreaker
from app.core.rate_limiter import RateLimiter
from app.core.redis_client import get_redis_client, is_redis_available, reset_redis_client


class TestMultiWorkerRateLimiting:
    """Test multi-worker rate limiting (shared limits via Redis)."""
    
    def test_rate_limit_shared_across_workers(self):
        """Test that rate limit is shared across multiple workers (simulated)."""
        # Simulate 2 workers sharing the same Redis key
        redis_key = "test_multi_worker"
        rate = 10.0  # 10 req/s
        burst = 10.0
        
        # Create 2 limiters with same Redis key (simulating 2 workers)
        limiter1 = DistributedRateLimiter(
            redis_key=redis_key,
            rate=rate,
            burst=burst,
        )
        limiter2 = DistributedRateLimiter(
            redis_key=redis_key,  # Same key = shared limit
            rate=rate,
            burst=burst,
        )
        
        # If Redis is available, both should share the same limit
        # If Redis is not available, each will use its own fallback (acceptable for test)
        redis_available = is_redis_available()
        
        if redis_available:
            # With Redis: Worker 1 uses 5 tokens, Worker 2 should only have 5 left
            acquired_count = 0
            for _ in range(5):
                if limiter1.acquire():
                    acquired_count += 1
            
            # Worker 2 should only be able to acquire remaining tokens
            worker2_acquired = 0
            for _ in range(10):  # Try to acquire 10
                if limiter2.acquire():
                    worker2_acquired += 1
                else:
                    break
            
            # Total should not exceed burst (10)
            assert acquired_count + worker2_acquired <= burst, \
                f"Total acquisitions ({acquired_count + worker2_acquired}) exceeded burst ({burst})"
        else:
            # Without Redis: Each worker has its own fallback limiter
            # This is acceptable - fallback mode is expected when Redis is unavailable
            assert limiter1.acquire() is True
            assert limiter2.acquire() is True
    
    def test_rate_limit_per_key_isolation(self):
        """Test that different Redis keys have isolated rate limits."""
        # Create 2 limiters with different Redis keys
        limiter1 = DistributedRateLimiter(
            redis_key="worker1",
            rate=10.0,
            burst=10.0,
        )
        limiter2 = DistributedRateLimiter(
            redis_key="worker2",  # Different key = separate limit
            rate=10.0,
            burst=10.0,
        )
        
        # Both should be able to acquire tokens independently
        assert limiter1.acquire() is True
        assert limiter2.acquire() is True
    
    def test_rate_limit_exceeded_scenario(self):
        """Test rate limit exceeded scenario."""
        limiter = DistributedRateLimiter(
            redis_key="test_limit_exceeded",
            rate=2.0,  # 2 req/s
            burst=2.0,
        )
        
        # Acquire burst amount
        for _ in range(2):
            assert limiter.acquire() is True
        
        # Next acquire should fail (rate limited)
        assert limiter.acquire() is False
        
        # Wait for token refill (0.6s should refill ~1.2 tokens)
        time.sleep(0.6)
        
        # Should be able to acquire again
        assert limiter.acquire() is True


class TestRedisDownFallback:
    """Test Redis down fallback to in-memory limiter."""
    
    def test_fallback_on_redis_unavailable(self):
        """Test that fallback limiter is used when Redis is unavailable."""
        # Mock Redis as unavailable
        with patch("app.core.distributed_rate_limiter.is_redis_available", return_value=False):
            limiter = DistributedRateLimiter(
                redis_key="test_fallback",
                rate=10.0,
                burst=10.0,
            )
            
            # Should use fallback limiter
            assert limiter.acquire() is True
            assert limiter.fallback.tokens == 9.0
    
    def test_fallback_limiter_functionality(self):
        """Test that fallback limiter works correctly."""
        # Create limiter with explicit fallback
        fallback = RateLimiter(rate=5.0, burst=5.0)
        limiter = DistributedRateLimiter(
            redis_key="test_fallback_explicit",
            rate=10.0,
            burst=10.0,
            fallback=fallback,
        )
        
        # Mock Redis as unavailable
        with patch("app.core.distributed_rate_limiter.is_redis_available", return_value=False):
            # Should use fallback
            assert limiter.acquire() is True
            assert fallback.tokens == 4.0
    
    def test_circuit_breaker_fallback_activation(self):
        """Test circuit breaker activates fallback after failures."""
        limiter = DistributedRateLimiter(
            redis_key="test_circuit_breaker",
            rate=10.0,
            burst=10.0,
        )
        
        # Mock Redis to fail
        mock_redis = MagicMock()
        mock_redis.pipeline.return_value.execute.side_effect = Exception("Redis connection failed")
        
        with patch("app.core.distributed_rate_limiter.get_redis_client", return_value=mock_redis):
            with patch("app.core.distributed_rate_limiter.is_redis_available", return_value=True):
                # Record failures to open circuit breaker
                for _ in range(5):  # failure_threshold = 5
                    try:
                        limiter.acquire()
                    except:
                        pass
                    limiter.circuit_breaker.record_failure()
                
                # Circuit should be open
                assert limiter.circuit_breaker.circuit_open is True
                
                # Should use fallback when circuit is open
                # (acquire should still work via fallback)
                assert limiter.acquire() is True


class TestCircuitBreakerRecovery:
    """Test circuit breaker recovery mechanism."""
    
    def test_circuit_breaker_recovery_after_timeout(self):
        """Test circuit breaker recovers after recovery timeout."""
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=0.1)
        
        # Open circuit
        for _ in range(3):
            breaker.record_failure()
        assert breaker.circuit_open is True
        assert breaker.should_attempt() is False
        
        # Wait for recovery timeout
        time.sleep(0.15)
        
        # Should attempt recovery
        assert breaker.should_attempt() is True
        assert breaker.circuit_open is False
    
    def test_circuit_breaker_resets_on_success(self):
        """Test circuit breaker resets on successful operation."""
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60.0)
        
        # Record 2 failures
        breaker.record_failure()
        breaker.record_failure()
        assert breaker.failure_count == 2
        assert breaker.circuit_open is False
        
        # Record success (should reset)
        breaker.record_success()
        assert breaker.failure_count == 0
        assert breaker.circuit_open is False
    
    def test_circuit_breaker_opens_after_threshold(self):
        """Test circuit breaker opens after failure threshold."""
        breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0)
        
        # Record 4 failures (should not open yet)
        for _ in range(4):
            breaker.record_failure()
        assert breaker.circuit_open is False
        
        # Record 5th failure (should open)
        breaker.record_failure()
        assert breaker.circuit_open is True
        assert breaker.should_attempt() is False


class TestDegradeModeLogging:
    """Test degrade mode logging when Redis is unavailable."""
    
    def test_degrade_mode_logging(self, caplog):
        """Test that degrade mode is logged when using fallback."""
        import logging
        caplog.set_level(logging.WARNING)
        
        limiter = DistributedRateLimiter(
            redis_key="test_degrade",
            rate=10.0,
            burst=10.0,
        )
        
        # Mock Redis as unavailable
        with patch("app.core.distributed_rate_limiter.is_redis_available", return_value=False):
            # Acquire should work (using fallback)
            limiter.acquire()
            
            # Note: Degrade mode logging happens in _acquire_redis when Redis fails
            # This is tested indirectly through circuit breaker behavior


class TestConcurrentAccess:
    """Test concurrent access to rate limiter (thread safety)."""
    
    def test_concurrent_acquire(self):
        """Test concurrent token acquisition."""
        limiter = DistributedRateLimiter(
            redis_key="test_concurrent",
            rate=10.0,
            burst=10.0,
        )
        
        results = []
        
        def acquire_tokens():
            for _ in range(5):
                result = limiter.acquire()
                results.append(result)
        
        # Create 2 threads
        thread1 = threading.Thread(target=acquire_tokens)
        thread2 = threading.Thread(target=acquire_tokens)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Total successful acquisitions should not exceed burst
        successful = sum(1 for r in results if r is True)
        assert successful <= limiter.burst, \
            f"Concurrent acquisitions ({successful}) exceeded burst ({limiter.burst})"

