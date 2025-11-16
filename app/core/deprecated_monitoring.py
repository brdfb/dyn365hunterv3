"""Monitoring for deprecated endpoints (G21 Phase 3).

Tracks deprecated endpoint usage metrics for migration monitoring.
"""

from typing import Dict, Any
from collections import defaultdict
from datetime import datetime
from app.core.logging import logger

# Deprecated endpoint metrics tracking (in-memory counters)
_deprecated_metrics = {
    "total_calls": 0,
    "calls_by_endpoint": defaultdict(int),  # endpoint -> count
    "calls_by_domain": defaultdict(int),  # domain -> count
    "daily_call_count": defaultdict(int),  # date -> count
    "weekly_call_count": defaultdict(int),  # week -> count
}


def track_deprecated_endpoint(endpoint: str, domain: str = None):
    """
    Track deprecated endpoint call for metrics.
    
    Args:
        endpoint: Endpoint name (e.g., "POST /leads/{domain}/notes")
        domain: Domain name (optional, for domain-specific tracking)
    """
    # Update metrics
    _deprecated_metrics["total_calls"] += 1
    _deprecated_metrics["calls_by_endpoint"][endpoint] += 1
    
    if domain:
        _deprecated_metrics["calls_by_domain"][domain] += 1
    
    # Track daily/weekly counts
    today = datetime.utcnow().date().isoformat()
    week = datetime.utcnow().strftime("%Y-W%W")
    _deprecated_metrics["daily_call_count"][today] += 1
    _deprecated_metrics["weekly_call_count"][week] += 1
    
    # Log warning
    logger.warning(
        "deprecated_endpoint_called",
        endpoint=endpoint,
        domain=domain,
        total_calls=_deprecated_metrics["total_calls"],
    )


def get_deprecated_metrics() -> Dict[str, Any]:
    """
    Get deprecated endpoint metrics.
    
    Returns:
        Dictionary with deprecated endpoint metrics
    """
    # Convert defaultdict to regular dict for JSON serialization
    calls_by_endpoint = dict(_deprecated_metrics["calls_by_endpoint"])
    calls_by_domain = dict(_deprecated_metrics["calls_by_domain"])
    daily_call_count = dict(_deprecated_metrics["daily_call_count"])
    weekly_call_count = dict(_deprecated_metrics["weekly_call_count"])
    
    # Calculate top endpoints and domains
    top_endpoints = sorted(
        calls_by_endpoint.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]  # Top 10
    
    top_domains = sorted(
        calls_by_domain.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]  # Top 10
    
    return {
        "total_calls": _deprecated_metrics["total_calls"],
        "calls_by_endpoint": calls_by_endpoint,
        "calls_by_domain": calls_by_domain,
        "daily_call_count": daily_call_count,
        "weekly_call_count": weekly_call_count,
        "top_endpoints": dict(top_endpoints),
        "top_domains": dict(top_domains),
    }


def reset_deprecated_metrics():
    """Reset deprecated endpoint metrics (for testing)."""
    global _deprecated_metrics
    _deprecated_metrics = {
        "total_calls": 0,
        "calls_by_endpoint": defaultdict(int),
        "calls_by_domain": defaultdict(int),
        "daily_call_count": defaultdict(int),
        "weekly_call_count": defaultdict(int),
    }

