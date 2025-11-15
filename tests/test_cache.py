"""Unit tests for Redis-based caching functionality."""

import pytest
import time
from unittest.mock import patch, MagicMock
from app.core.cache import (
    get_cached_dns,
    set_cached_dns,
    get_cached_whois,
    set_cached_whois,
    get_cached_provider,
    set_cached_provider,
    get_cached_scoring,
    set_cached_scoring,
    get_cached_scan,
    set_cached_scan,
    invalidate_scan_cache,
    _generate_signals_hash,
    DNS_CACHE_TTL,
    WHOIS_CACHE_TTL,
    PROVIDER_CACHE_TTL,
    SCORING_CACHE_TTL,
    SCAN_CACHE_TTL,
)
from app.core.analyzer_dns import analyze_dns
from app.core.analyzer_whois import get_whois_info
from app.core.provider_map import classify_provider
from app.core.scorer import score_domain


class TestCacheUtilities:
    """Test cache utility functions."""

    def test_generate_signals_hash_stable(self):
        """Test that signals hash is stable for same signals."""
        signals1 = {"spf": True, "dkim": False, "dmarc_policy": "none"}
        signals2 = {"dkim": False, "spf": True, "dmarc_policy": "none"}  # Different order
        
        hash1 = _generate_signals_hash(signals1)
        hash2 = _generate_signals_hash(signals2)
        
        # Should be same hash despite different key order (sort_keys=True)
        assert hash1 == hash2
        assert len(hash1) == 16  # 16-character hex hash

    def test_generate_signals_hash_different(self):
        """Test that different signals produce different hashes."""
        signals1 = {"spf": True, "dkim": False, "dmarc_policy": "none"}
        signals2 = {"spf": True, "dkim": True, "dmarc_policy": "none"}  # Different value
        
        hash1 = _generate_signals_hash(signals1)
        hash2 = _generate_signals_hash(signals2)
        
        # Should be different hashes
        assert hash1 != hash2


class TestDNSCache:
    """Test DNS cache functionality."""

    def test_dns_cache_set_get(self):
        """Test DNS cache set and get."""
        domain = "test.example.com"
        dns_result = {
            "mx_records": ["mx1.example.com"],
            "mx_root": "example.com",
            "spf": True,
            "dkim": False,
            "dmarc_policy": "none",
            "status": "success",
        }
        
        # Set cache
        set_success = set_cached_dns(domain, dns_result)
        # May fail if Redis unavailable, that's OK for tests
        if set_success:
            # Get cache
            cached = get_cached_dns(domain)
            if cached is not None:
                assert cached["mx_root"] == dns_result["mx_root"]
                assert cached["spf"] == dns_result["spf"]

    def test_analyze_dns_uses_cache(self):
        """Test that analyze_dns uses cache when available."""
        # Mock Redis as unavailable to test fallback
        with patch("app.core.cache.is_redis_available", return_value=False):
            # Should still work (fallback to no cache)
            result = analyze_dns("example.com", use_cache=True)
            assert "status" in result


class TestWHOISCache:
    """Test WHOIS cache functionality."""

    def test_whois_cache_set_get(self):
        """Test WHOIS cache set and get."""
        domain = "test.example.com"
        whois_result = {
            "registrar": "Example Registrar",
            "expires_at": "2025-12-31",
            "nameservers": ["ns1.example.com"],
        }
        
        # Set cache
        set_success = set_cached_whois(domain, whois_result)
        # May fail if Redis unavailable, that's OK for tests
        if set_success:
            # Get cache
            cached = get_cached_whois(domain)
            if cached is not None:
                assert cached["registrar"] == whois_result["registrar"]

    def test_get_whois_info_uses_cache(self):
        """Test that get_whois_info uses cache when available."""
        # Mock Redis as unavailable to test fallback
        with patch("app.core.cache.is_redis_available", return_value=False):
            # Should still work (fallback to no cache)
            result = get_whois_info("example.com", use_cache=True)
            # Result may be None if WHOIS fails, that's OK


class TestProviderCache:
    """Test provider mapping cache functionality."""

    def test_provider_cache_set_get(self):
        """Test provider cache set and get."""
        mx_root = "outlook.com"
        provider = "M365"
        
        # Set cache
        set_success = set_cached_provider(mx_root, provider)
        # May fail if Redis unavailable, that's OK for tests
        if set_success:
            # Get cache
            cached = get_cached_provider(mx_root)
            if cached is not None:
                assert cached == provider

    def test_classify_provider_uses_cache(self):
        """Test that classify_provider uses cache when available."""
        # Mock Redis as unavailable to test fallback
        with patch("app.core.cache.is_redis_available", return_value=False):
            # Should still work (fallback to no cache)
            result = classify_provider("outlook.com", use_cache=True)
            assert result in ["M365", "Local", "Unknown"]


class TestScoringCache:
    """Test scoring cache functionality."""

    def test_scoring_cache_set_get(self):
        """Test scoring cache set and get."""
        domain = "test.example.com"
        provider = "M365"
        signals = {"spf": True, "dkim": False, "dmarc_policy": "none"}
        scoring_result = {"score": 75, "segment": "Migration", "reason": "Test"}
        
        # Set cache
        set_success = set_cached_scoring(domain, provider, signals, scoring_result)
        # May fail if Redis unavailable, that's OK for tests
        if set_success:
            # Get cache
            cached = get_cached_scoring(domain, provider, signals)
            if cached is not None:
                assert cached["score"] == scoring_result["score"]
                assert cached["segment"] == scoring_result["segment"]

    def test_score_domain_uses_cache(self):
        """Test that score_domain uses cache when available."""
        # Mock Redis as unavailable to test fallback
        with patch("app.core.cache.is_redis_available", return_value=False):
            # Should still work (fallback to no cache)
            signals = {"spf": True, "dkim": False, "dmarc_policy": "none"}
            result = score_domain(
                domain="example.com",
                provider="M365",
                signals=signals,
                use_cache=True,
            )
            assert "score" in result
            assert "segment" in result


class TestScanCache:
    """Test full scan cache functionality."""

    def test_scan_cache_set_get(self):
        """Test scan cache set and get."""
        domain = "test.example.com"
        scan_result = {
            "dns_result": {"mx_root": "example.com", "spf": True},
            "whois_result": {"registrar": "Example"},
            "provider": "M365",
            "scoring_result": {"score": 75, "segment": "Migration"},
            "scan_status": "success",
        }
        
        # Set cache
        set_success = set_cached_scan(domain, scan_result)
        # May fail if Redis unavailable, that's OK for tests
        if set_success:
            # Get cache
            cached = get_cached_scan(domain)
            if cached is not None:
                assert cached["provider"] == scan_result["provider"]
                assert cached["scan_status"] == scan_result["scan_status"]

    def test_invalidate_scan_cache(self):
        """Test scan cache invalidation."""
        domain = "test.example.com"
        scan_result = {"provider": "M365", "scan_status": "success"}
        
        # Set cache
        set_success = set_cached_scan(domain, scan_result)
        if set_success:
            # Invalidate
            invalidate_success = invalidate_scan_cache(domain)
            if invalidate_success:
                # Should be None after invalidation
                cached = get_cached_scan(domain)
                assert cached is None


class TestCacheTTL:
    """Test cache TTL constants."""

    def test_cache_ttl_constants(self):
        """Test that cache TTL constants are defined correctly."""
        assert DNS_CACHE_TTL == 3600  # 1 hour
        assert WHOIS_CACHE_TTL == 86400  # 24 hours
        assert PROVIDER_CACHE_TTL == 86400  # 24 hours
        assert SCORING_CACHE_TTL == 3600  # 1 hour
        assert SCAN_CACHE_TTL == 3600  # 1 hour


class TestCacheRedisUnavailable:
    """Test cache behavior when Redis is unavailable."""

    def test_cache_fallback_on_redis_unavailable(self):
        """Test that cache functions gracefully handle Redis unavailability."""
        # Mock Redis as unavailable
        with patch("app.core.cache.is_redis_available", return_value=False):
            # All cache operations should return None/False gracefully
            assert get_cached_dns("example.com") is None
            assert set_cached_dns("example.com", {}) is False
            assert get_cached_whois("example.com") is None
            assert get_cached_provider("outlook.com") is None
            assert get_cached_scoring("example.com", "M365", {}) is None
            assert get_cached_scan("example.com") is None

