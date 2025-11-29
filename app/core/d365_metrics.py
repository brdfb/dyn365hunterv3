"""Dynamics 365 metrics tracking module (Phase 3)."""

from typing import Dict, Any
from threading import Lock

# D365 metrics tracking (in-memory counters)
_d365_metrics = {
    "push_requested_total": 0,
    "push_success_total": 0,
    "push_failed_total": 0,
    "push_queued_total": 0,
    "last_push_duration": 0.0,  # Last push duration in seconds
    "push_durations": [],  # Last 100 push durations for average calculation
    # Retry metrics (PROD FINAL)
    "retry_total": 0,  # Total retry attempts
    "retry_success_total": 0,  # Successful retries
    "retry_failed_total": 0,  # Failed retries (after max retries)
    "error_by_category": {  # Error counts by category
        "auth": 0,
        "rate_limit": 0,
        "validation": 0,
        "network": 0,
        "unknown": 0,
    },
    "dlq_total": 0,  # Dead letter queue count (max retries exhausted)
}

_metrics_lock = Lock()


def track_push_requested():
    """Track D365 push request."""
    with _metrics_lock:
        _d365_metrics["push_requested_total"] += 1
        _d365_metrics["push_queued_total"] += 1


def track_push_success(duration: float):
    """Track successful D365 push."""
    with _metrics_lock:
        _d365_metrics["push_success_total"] += 1
        _d365_metrics["push_queued_total"] = max(0, _d365_metrics["push_queued_total"] - 1)
        _d365_metrics["last_push_duration"] = duration
        
        # Keep last 100 durations for average calculation
        _d365_metrics["push_durations"].append(duration)
        if len(_d365_metrics["push_durations"]) > 100:
            _d365_metrics["push_durations"].pop(0)


def track_push_failed():
    """Track failed D365 push."""
    with _metrics_lock:
        _d365_metrics["push_failed_total"] += 1
        _d365_metrics["push_queued_total"] = max(0, _d365_metrics["push_queued_total"] - 1)


def track_retry_attempt():
    """Track retry attempt."""
    with _metrics_lock:
        _d365_metrics["retry_total"] += 1


def track_retry_success():
    """Track successful retry."""
    with _metrics_lock:
        _d365_metrics["retry_success_total"] += 1


def track_retry_failed():
    """Track failed retry (after max retries)."""
    with _metrics_lock:
        _d365_metrics["retry_failed_total"] += 1


def track_error_category(category: str):
    """Track error by category."""
    with _metrics_lock:
        if category in _d365_metrics["error_by_category"]:
            _d365_metrics["error_by_category"][category] += 1


def track_dlq():
    """Track dead letter queue entry (max retries exhausted)."""
    with _metrics_lock:
        _d365_metrics["dlq_total"] += 1


def get_d365_metrics() -> Dict[str, Any]:
    """Get current D365 metrics."""
    with _metrics_lock:
        # Calculate average push duration
        avg_duration = 0.0
        if _d365_metrics["push_durations"]:
            avg_duration = sum(_d365_metrics["push_durations"]) / len(_d365_metrics["push_durations"])
        
        # Calculate retry success rate
        retry_success_rate = 0.0
        if _d365_metrics["retry_total"] > 0:
            retry_success_rate = (_d365_metrics["retry_success_total"] / _d365_metrics["retry_total"]) * 100
        
        return {
            "push_requested_total": _d365_metrics["push_requested_total"],
            "push_success_total": _d365_metrics["push_success_total"],
            "push_failed_total": _d365_metrics["push_failed_total"],
            "push_queued_total": _d365_metrics["push_queued_total"],
            "last_push_duration": _d365_metrics["last_push_duration"],
            "avg_push_duration": avg_duration,
            # Retry metrics (PROD FINAL)
            "retry_total": _d365_metrics["retry_total"],
            "retry_success_total": _d365_metrics["retry_success_total"],
            "retry_failed_total": _d365_metrics["retry_failed_total"],
            "retry_success_rate": retry_success_rate,
            "error_by_category": _d365_metrics["error_by_category"].copy(),
            "dlq_total": _d365_metrics["dlq_total"],
        }


def reset_d365_metrics():
    """Reset D365 metrics (for testing)."""
    with _metrics_lock:
        _d365_metrics["push_requested_total"] = 0
        _d365_metrics["push_success_total"] = 0
        _d365_metrics["push_failed_total"] = 0
        _d365_metrics["push_queued_total"] = 0
        _d365_metrics["last_push_duration"] = 0.0
        _d365_metrics["push_durations"] = []
        _d365_metrics["retry_total"] = 0
        _d365_metrics["retry_success_total"] = 0
        _d365_metrics["retry_failed_total"] = 0
        _d365_metrics["error_by_category"] = {
            "auth": 0,
            "rate_limit": 0,
            "validation": 0,
            "network": 0,
            "unknown": 0,
        }
        _d365_metrics["dlq_total"] = 0

