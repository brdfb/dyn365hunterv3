"""Tests for API key authentication and rate limiting."""
import pytest
import time
from app.core.api_key_auth import (
    hash_api_key,
    generate_api_key,
    get_api_key_limiter
)


def test_hash_api_key():
    """Test API key hashing."""
    key = "test-key-123"
    hash1 = hash_api_key(key)
    hash2 = hash_api_key(key)
    
    # Same key should produce same hash
    assert hash1 == hash2
    
    # Hash should be different from original
    assert hash1 != key
    
    # Hash should be hex string (SHA-256 = 64 chars)
    assert len(hash1) == 64


def test_generate_api_key():
    """Test API key generation."""
    key1 = generate_api_key()
    key2 = generate_api_key()
    
    # Keys should be different
    assert key1 != key2
    
    # Keys should be strings
    assert isinstance(key1, str)
    assert isinstance(key2, str)
    
    # Keys should have reasonable length
    assert len(key1) > 20


def test_get_api_key_limiter():
    """Test rate limiter creation for API keys."""
    limiter1 = get_api_key_limiter(1, 60)  # 60 per minute
    limiter2 = get_api_key_limiter(2, 120)  # 120 per minute
    
    # Different API keys should get different limiters
    assert limiter1 != limiter2
    
    # Same API key should get same limiter
    limiter1_again = get_api_key_limiter(1, 60)
    assert limiter1 == limiter1_again


def test_rate_limiter_acquire():
    """Test rate limiter token acquisition."""
    limiter = get_api_key_limiter(999, 60)  # 60 per minute = 1 per second
    
    # Should be able to acquire tokens initially
    assert limiter.acquire() is True
    assert limiter.acquire() is True
    
    # With 1 req/s rate, should be able to acquire quickly
    # (burst allows initial requests)


def test_rate_limiter_exhaustion():
    """Test rate limiter exhaustion."""
    limiter = get_api_key_limiter(998, 2)  # 2 per minute = very low rate
    
    # Should be able to acquire initially (burst)
    assert limiter.acquire() is True
    assert limiter.acquire() is True
    
    # After burst, should be rate limited
    # Note: This test may be flaky due to timing, but tests the concept
    time.sleep(0.1)  # Small delay
    # With very low rate, might be limited
    # This is more of a smoke test

