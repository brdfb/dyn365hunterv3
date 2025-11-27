"""Tests for retry utilities (exponential backoff with jitter)."""

import pytest
from app.core.retry_utils import compute_backoff_with_jitter, clamp_retry_after


def test_compute_backoff_with_jitter_attempt_0():
    """Test backoff calculation for first retry (attempt 0)."""
    backoff = compute_backoff_with_jitter(base_seconds=60, attempt=0, max_seconds=3600)
    
    # Should be ~60s + jitter (0-10s)
    assert 60.0 <= backoff <= 70.0


def test_compute_backoff_with_jitter_attempt_1():
    """Test backoff calculation for second retry (attempt 1)."""
    backoff = compute_backoff_with_jitter(base_seconds=60, attempt=1, max_seconds=3600)
    
    # Should be ~120s + jitter (0-10s)
    assert 120.0 <= backoff <= 130.0


def test_compute_backoff_with_jitter_attempt_3():
    """Test backoff calculation for fourth retry (attempt 3)."""
    backoff = compute_backoff_with_jitter(base_seconds=60, attempt=3, max_seconds=3600)
    
    # Should be ~480s + jitter (0-10s)
    assert 480.0 <= backoff <= 490.0


def test_compute_backoff_with_jitter_capped():
    """Test backoff is capped at max_seconds."""
    backoff = compute_backoff_with_jitter(base_seconds=60, attempt=10, max_seconds=3600)
    
    # Should be capped at 3600s + jitter (0-10s)
    assert 3600.0 <= backoff <= 3610.0


def test_compute_backoff_with_jitter_has_jitter():
    """Test that backoff includes jitter (multiple calls return different values)."""
    backoffs = [
        compute_backoff_with_jitter(base_seconds=60, attempt=0, max_seconds=3600)
        for _ in range(10)
    ]
    
    # All should be in range
    assert all(60.0 <= b <= 70.0 for b in backoffs)
    
    # Should have some variation (jitter)
    # Note: Very unlikely all 10 values are identical
    unique_values = len(set(round(b, 1) for b in backoffs))
    assert unique_values > 1, "Jitter should create variation in backoff values"


def test_compute_backoff_with_jitter_custom_jitter():
    """Test custom jitter_max parameter."""
    backoff = compute_backoff_with_jitter(
        base_seconds=60,
        attempt=0,
        max_seconds=3600,
        jitter_max=5.0
    )
    
    # Should be ~60s + jitter (0-5s)
    assert 60.0 <= backoff <= 65.0


def test_clamp_retry_after_normal():
    """Test clamp_retry_after with normal value."""
    retry_time = clamp_retry_after(30, min_seconds=1, max_seconds=3600)
    
    # Should be ~30s + jitter (0-10s)
    assert 30.0 <= retry_time <= 40.0


def test_clamp_retry_after_clamped_min():
    """Test clamp_retry_after clamps to minimum."""
    retry_time = clamp_retry_after(-5, min_seconds=1, max_seconds=3600)
    
    # Should be clamped to 1s + jitter (0-10s)
    assert 1.0 <= retry_time <= 11.0


def test_clamp_retry_after_clamped_max():
    """Test clamp_retry_after clamps to maximum."""
    retry_time = clamp_retry_after(5000, min_seconds=1, max_seconds=3600)
    
    # Should be clamped to 3600s + jitter (0-10s)
    assert 3600.0 <= retry_time <= 3610.0


def test_clamp_retry_after_none():
    """Test clamp_retry_after with None (uses default)."""
    retry_time = clamp_retry_after(None, min_seconds=1, max_seconds=3600)
    
    # Should use min_seconds (1s) + jitter (0-10s)
    assert 1.0 <= retry_time <= 11.0


def test_clamp_retry_after_has_jitter():
    """Test that clamp_retry_after includes jitter."""
    retry_times = [
        clamp_retry_after(30, min_seconds=1, max_seconds=3600)
        for _ in range(10)
    ]
    
    # All should be in range
    assert all(30.0 <= r <= 40.0 for r in retry_times)
    
    # Should have some variation (jitter)
    unique_values = len(set(round(r, 1) for r in retry_times))
    assert unique_values > 1, "Jitter should create variation in retry times"

