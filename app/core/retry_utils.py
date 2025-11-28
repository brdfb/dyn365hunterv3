"""Retry utilities for exponential backoff with jitter."""

import random
from typing import Union


def compute_backoff_with_jitter(
    base_seconds: int,
    attempt: int,
    max_seconds: int = 3600,
    jitter_max: float = 10.0
) -> float:
    """
    Compute exponential backoff with jitter.
    
    Formula: min(base_seconds * (2 ** attempt), max_seconds) + random(0, jitter_max)
    
    Args:
        base_seconds: Base backoff time in seconds (e.g., 60 for 1 minute)
        attempt: Retry attempt number (0-based or 1-based, typically 0-based for first retry)
        max_seconds: Maximum backoff time in seconds (default: 3600 = 1 hour)
        jitter_max: Maximum jitter in seconds (default: 10.0)
    
    Returns:
        Backoff time in seconds (base backoff + jitter)
    
    Examples:
        >>> compute_backoff_with_jitter(60, 0)  # First retry: ~60-70s
        >>> compute_backoff_with_jitter(60, 1)  # Second retry: ~120-130s
        >>> compute_backoff_with_jitter(60, 3)  # Fourth retry: ~480-490s
        >>> compute_backoff_with_jitter(60, 10) # Eleventh retry: 3600s (capped) + jitter
    """
    # Exponential backoff: base * (2 ** attempt)
    backoff = base_seconds * (2 ** attempt)
    
    # Cap at max_seconds (before jitter to ensure total doesn't exceed max significantly)
    backoff = min(backoff, max_seconds)
    
    # Add random jitter to prevent thundering herd
    jitter = random.uniform(0, jitter_max)
    
    # Final result: backoff + jitter (may slightly exceed max_seconds due to jitter, but that's acceptable)
    return backoff + jitter


def clamp_retry_after(
    retry_after: Union[int, float, None],
    min_seconds: int = 1,
    max_seconds: int = 3600,
    jitter_max: float = 10.0
) -> float:
    """
    Clamp Retry-After header value and add jitter.
    
    Args:
        retry_after: Retry-After header value in seconds (can be None)
        min_seconds: Minimum retry time in seconds (default: 1)
        max_seconds: Maximum retry time in seconds (default: 3600)
        jitter_max: Maximum jitter in seconds (default: 10.0)
    
    Returns:
        Clamped retry time with jitter in seconds
    
    Examples:
        >>> clamp_retry_after(30)  # 30s + jitter
        >>> clamp_retry_after(5000)  # 3600s (capped) + jitter
        >>> clamp_retry_after(-5)  # 1s (clamped) + jitter
        >>> clamp_retry_after(None)  # 1s (default) + jitter
    """
    if retry_after is None:
        retry_after = min_seconds
    else:
        # Clamp between min and max
        retry_after = max(min_seconds, min(int(retry_after), max_seconds))
    
    # Add random jitter to prevent thundering herd
    jitter = random.uniform(0, jitter_max)
    
    return retry_after + jitter

