"""Partner Center metrics tracking module."""

from typing import Dict, Any
from threading import Lock

# Partner Center metrics tracking (in-memory counters)
_partner_center_metrics = {
    "sync_runs": 0,
    "sync_success": 0,
    "sync_failed": 0,
    "sync_skipped": 0,  # Feature flag disabled
    "total_fetched": 0,
    "total_inserted": 0,
    "total_skipped": 0,
    "total_failed": 0,
    "last_sync_duration": 0.0,  # Last sync duration in seconds
    "sync_durations": [],  # Last 100 sync durations for average calculation
}

_metrics_lock = Lock()


def track_sync_start():
    """Track sync run start."""
    with _metrics_lock:
        _partner_center_metrics["sync_runs"] += 1


def track_sync_success(duration: float, fetched: int, inserted: int, skipped: int):
    """Track successful sync run."""
    with _metrics_lock:
        _partner_center_metrics["sync_success"] += 1
        _partner_center_metrics["total_fetched"] += fetched
        _partner_center_metrics["total_inserted"] += inserted
        _partner_center_metrics["total_skipped"] += skipped
        _partner_center_metrics["last_sync_duration"] = duration
        
        # Track last 100 durations for average
        _partner_center_metrics["sync_durations"].append(duration)
        if len(_partner_center_metrics["sync_durations"]) > 100:
            _partner_center_metrics["sync_durations"] = _partner_center_metrics["sync_durations"][-100:]


def track_sync_failed(duration: float):
    """Track failed sync run."""
    with _metrics_lock:
        _partner_center_metrics["sync_failed"] += 1
        _partner_center_metrics["last_sync_duration"] = duration


def track_sync_skipped():
    """Track skipped sync run (feature flag disabled)."""
    with _metrics_lock:
        _partner_center_metrics["sync_skipped"] += 1


def track_sync_failure(failed_count: int):
    """Track referral processing failures."""
    with _metrics_lock:
        _partner_center_metrics["total_failed"] += failed_count


def get_partner_center_metrics() -> Dict[str, Any]:
    """
    Get Partner Center sync metrics.
    
    Returns:
        Dictionary with Partner Center metrics
    """
    with _metrics_lock:
        durations = _partner_center_metrics["sync_durations"]
        avg_duration = (
            sum(durations) / len(durations) if durations else 0.0
        )
        
        total_runs = (
            _partner_center_metrics["sync_success"]
            + _partner_center_metrics["sync_failed"]
            + _partner_center_metrics["sync_skipped"]
        )
        success_rate = (
            (_partner_center_metrics["sync_success"] / total_runs * 100)
            if total_runs > 0
            else 0.0
        )
        
        return {
            "sync_runs": _partner_center_metrics["sync_runs"],
            "sync_success": _partner_center_metrics["sync_success"],
            "sync_failed": _partner_center_metrics["sync_failed"],
            "sync_skipped": _partner_center_metrics["sync_skipped"],
            "success_rate": round(success_rate, 2),
            "total_fetched": _partner_center_metrics["total_fetched"],
            "total_inserted": _partner_center_metrics["total_inserted"],
            "total_skipped": _partner_center_metrics["total_skipped"],
            "total_failed": _partner_center_metrics["total_failed"],
            "last_sync_duration": round(_partner_center_metrics["last_sync_duration"], 2),
            "avg_sync_duration": round(avg_duration, 2),
        }


def reset_partner_center_metrics():
    """Reset Partner Center metrics (for testing)."""
    global _partner_center_metrics
    with _metrics_lock:
        _partner_center_metrics = {
            "sync_runs": 0,
            "sync_success": 0,
            "sync_failed": 0,
            "sync_skipped": 0,
            "total_fetched": 0,
            "total_inserted": 0,
            "total_skipped": 0,
            "total_failed": 0,
            "last_sync_duration": 0.0,
            "sync_durations": [],
        }

