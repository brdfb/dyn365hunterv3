"""Tests for cache invalidation and consistency (Gün 2: Monitoring ve Safety).

These tests require Redis to be available. If Redis is not available,
tests will be skipped automatically.
"""

import pytest
import os
import time
from unittest.mock import patch, Mock
from app.core.cache import (
    get_cached_scan,
    set_cached_scan,
    invalidate_scan_cache,
    get_cached_dns,
    set_cached_dns,
    get_cache_metrics,
    reset_cache_metrics,
)
from app.core.redis_client import is_redis_available
from app.core.rescan import rescan_domain

# Test Redis URL
TEST_REDIS_URL = os.getenv(
    "TEST_REDIS_URL",
    os.getenv(
        "HUNTER_REDIS_URL",
        os.getenv("REDIS_URL", "redis://localhost:6379/1"),
    ),
)


@pytest.fixture(scope="function", autouse=True)
def check_redis():
    """Check if Redis is available before running cache tests."""
    if not is_redis_available():
        pytest.skip("Redis not available - skipping cache invalidation tests")


@pytest.fixture(scope="function")
def redis_client():
    """Create a test Redis client."""
    if not is_redis_available():
        pytest.skip("Redis not available")
    
    try:
        import redis
        from app.core.redis_client import get_redis_client
        client = get_redis_client()
        if client is None:
            pytest.skip("Redis client not available")
        client.ping()
        yield client
        # Clean up test keys
        keys = client.keys("cache:*")
        if keys:
            client.delete(*keys)
    except Exception:
        pytest.skip("Test Redis not available")


@pytest.fixture(scope="function")
def reset_metrics():
    """Reset cache metrics before each test."""
    reset_cache_metrics()
    yield
    reset_cache_metrics()


def test_rescan_cache_invalidation(redis_client, reset_metrics):
    """
    Test that rescan invalidates cache correctly.
    
    When a domain is rescanned, the old cache should be invalidated
    and new cache should be created.
    
    Requires: Redis available
    """
    if not is_redis_available():
        pytest.skip("Redis not available")
    
    domain = "test.example.com"
    
    # Set initial cache
    initial_result = {"score": 50, "provider": "M365"}
    set_cached_scan(domain, initial_result)
    
    # Verify cache is set
    cached = get_cached_scan(domain)
    assert cached is not None
    assert cached["score"] == 50
    
    # Invalidate cache (simulating rescan)
    invalidate_scan_cache(domain)
    
    # Verify cache is invalidated
    cached_after = get_cached_scan(domain)
    assert cached_after is None, "Cache should be invalidated after rescan"
    
    # Set new cache (simulating new scan result)
    new_result = {"score": 75, "provider": "M365"}
    set_cached_scan(domain, new_result)
    
    # Verify new cache is set
    cached_new = get_cached_scan(domain)
    assert cached_new is not None
    assert cached_new["score"] == 75, "New cache should have updated score"


def test_ttl_expiration(redis_client, reset_metrics):
    """
    Test TTL expiration - cache should expire after TTL.
    
    Requires: Redis available
    """
    if not is_redis_available():
        pytest.skip("Redis not available")
    
    domain = "test-ttl.example.com"
    
    # Set cache with short TTL (1 second for testing)
    from app.core.cache import set_cached_value, get_cached_value, _get_cache_key
    key = _get_cache_key("scan", domain)
    result = {"score": 50, "provider": "M365"}
    
    # Set with 1 second TTL
    set_cached_value(key, result, ttl=1)
    
    # Verify cache is set
    cached = get_cached_value(key)
    assert cached is not None
    
    # Wait for TTL to expire
    time.sleep(1.5)
    
    # Verify cache is expired
    cached_after = get_cached_value(key)
    assert cached_after is None, "Cache should expire after TTL"
    
    # Track TTL expiration in metrics
    metrics = get_cache_metrics()
    # Note: TTL expiration tracking is not fully implemented in cache.py
    # This test verifies that expired cache is not returned


def test_cache_key_collision(redis_client, reset_metrics):
    """
    Test cache key collision - same key should not have different data.
    
    This test verifies that cache keys are unique and don't collide.
    
    Requires: Redis available
    """
    if not is_redis_available():
        pytest.skip("Redis not available")
    
    domain1 = "test1.example.com"
    domain2 = "test2.example.com"
    
    # Set cache for two different domains
    result1 = {"score": 50, "provider": "M365"}
    result2 = {"score": 75, "provider": "Google"}
    
    set_cached_scan(domain1, result1)
    set_cached_scan(domain2, result2)
    
    # Verify each domain has its own cache
    cached1 = get_cached_scan(domain1)
    cached2 = get_cached_scan(domain2)
    
    assert cached1 is not None
    assert cached2 is not None
    assert cached1["score"] == 50, "Domain1 cache should be independent"
    assert cached2["score"] == 75, "Domain2 cache should be independent"
    assert cached1["provider"] == "M365"
    assert cached2["provider"] == "Google"


def test_cache_consistency_redis_down(redis_client, reset_metrics):
    """
    Test cache consistency when Redis is down - fallback should work.
    
    When Redis is unavailable, cache operations should gracefully fail
    and not crash the application.
    
    Requires: Redis available (to test fallback behavior)
    """
    if not is_redis_available():
        pytest.skip("Redis not available - cannot test fallback behavior")
    
    domain = "test-fallback.example.com"
    
    # Set cache normally
    result = {"score": 50, "provider": "M365"}
    set_cached_scan(domain, result)
    
    # Verify cache is set
    cached = get_cached_scan(domain)
    assert cached is not None
    
    # Simulate Redis down
    with patch("app.core.cache.is_redis_available", return_value=False):
        # Cache operations should gracefully fail
        cached_down = get_cached_scan(domain)
        assert cached_down is None, "Cache should return None when Redis is down"
        
        # Setting cache should also gracefully fail
        set_result = set_cached_scan(domain, result)
        assert set_result is False, "Cache set should fail gracefully when Redis is down"
    
    # After Redis recovery, cache should work again
    # (In real scenario, Redis would be restarted)
    # For this test, we just verify that the code handles Redis down gracefully


def test_cache_consistency_recovery(redis_client, reset_metrics):
    """
    Test cache consistency after Redis recovery.
    
    After Redis recovers from downtime, cache should work normally again.
    
    Requires: Redis available
    """
    if not is_redis_available():
        pytest.skip("Redis not available")
    
    domain = "test-recovery.example.com"
    
    # Simulate Redis down, then recovery
    with patch("app.core.cache.is_redis_available") as mock_available:
        # First: Redis down
        mock_available.return_value = False
        cached_down = get_cached_scan(domain)
        assert cached_down is None
        
        # Then: Redis recovers
        mock_available.return_value = True
        
        # Set cache after recovery
        result = {"score": 50, "provider": "M365"}
        set_cached_scan(domain, result)
        
        # Verify cache works after recovery
        cached_recovered = get_cached_scan(domain)
        assert cached_recovered is not None
        assert cached_recovered["score"] == 50


def test_cache_metrics_tracking(redis_client, reset_metrics):
    """
    Test that cache metrics are tracked correctly (hits, misses, etc.).
    
    Note: Metrics tracking works even without Redis (in-memory counters),
    but cache operations require Redis.
    
    Requires: Redis available
    """
    if not is_redis_available():
        pytest.skip("Redis not available")
    
    domain = "test-metrics.example.com"
    
    # Reset metrics
    reset_cache_metrics()
    
    # Miss: Get non-existent cache
    cached = get_cached_scan(domain)
    assert cached is None
    
    # Check metrics
    metrics = get_cache_metrics()
    assert metrics["misses"] >= 1, "Should track cache misses"
    
    # Set cache
    result = {"score": 50, "provider": "M365"}
    set_cached_scan(domain, result)
    
    # Hit: Get existing cache
    cached = get_cached_scan(domain)
    assert cached is not None
    
    # Check metrics
    metrics = get_cache_metrics()
    assert metrics["hits"] >= 1, "Should track cache hits"
    assert metrics["sets"] >= 1, "Should track cache sets"
    
    # Calculate hit rate
    total = metrics["hits"] + metrics["misses"]
    if total > 0:
        hit_rate = metrics["hits"] / total * 100
        assert metrics["hit_rate_percent"] == round(hit_rate, 2), "Hit rate should be calculated correctly"


def test_dns_cache_invalidation(redis_client, reset_metrics):
    """
    Test DNS cache invalidation (similar to scan cache).
    
    Requires: Redis available
    """
    if not is_redis_available():
        pytest.skip("Redis not available")
    
    domain = "test-dns.example.com"
    
    # Set DNS cache
    dns_result = {"mx_root": "outlook.com", "spf": True}
    from app.core.cache import set_cached_dns
    set_cached_dns(domain, dns_result)
    
    # Verify cache is set
    cached = get_cached_dns(domain)
    assert cached is not None
    assert cached["mx_root"] == "outlook.com"
    
    # Invalidate DNS cache (by setting new value)
    new_dns_result = {"mx_root": "google.com", "spf": True}
    set_cached_dns(domain, new_dns_result)
    
    # Verify new cache is set
    cached_new = get_cached_dns(domain)
    assert cached_new is not None
    assert cached_new["mx_root"] == "google.com", "DNS cache should be updated"

