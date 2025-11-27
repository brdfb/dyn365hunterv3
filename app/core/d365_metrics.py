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


def get_d365_metrics() -> Dict[str, Any]:
    """Get current D365 metrics."""
    with _metrics_lock:
        # Calculate average push duration
        avg_duration = 0.0
        if _d365_metrics["push_durations"]:
            avg_duration = sum(_d365_metrics["push_durations"]) / len(_d365_metrics["push_durations"])
        
        return {
            "push_requested_total": _d365_metrics["push_requested_total"],
            "push_success_total": _d365_metrics["push_success_total"],
            "push_failed_total": _d365_metrics["push_failed_total"],
            "push_queued_total": _d365_metrics["push_queued_total"],
            "last_push_duration": _d365_metrics["last_push_duration"],
            "avg_push_duration": avg_duration,
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

