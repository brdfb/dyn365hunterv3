"""Error tracking with Sentry integration."""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from typing import Dict, Any, Optional
from collections import defaultdict
from datetime import datetime
from app.config import settings

# Initialize Sentry only in production/staging environments
if settings.environment in {"production", "staging"}:
    if hasattr(settings, "sentry_dsn") and settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=0.1,  # 10% of transactions
            environment=settings.environment,
        )

# Error metrics tracking (in-memory counters)
_error_metrics = {
    "total_errors": 0,
    "errors_by_component": defaultdict(int),  # alembic, redis, db, dns, whois, etc.
    "errors_by_severity": defaultdict(int),  # critical, error, warning
    "daily_error_count": defaultdict(int),  # date -> count
    "weekly_error_count": defaultdict(int),  # week -> count
}


def categorize_error(error: Exception, component: Optional[str] = None) -> Dict[str, str]:
    """
    Categorize error for Sentry tracking.
    
    Args:
        error: Exception object
        component: Component name (alembic, redis, db, dns, whois, etc.)
        
    Returns:
        Dictionary with error categorization
    """
    error_type = type(error).__name__
    error_str = str(error).lower()
    
    # Auto-detect component if not provided
    if not component:
        if "alembic" in error_str or "migration" in error_str:
            component = "alembic"
        elif "redis" in error_str:
            component = "redis"
        elif "database" in error_str or "db" in error_str or "sql" in error_str:
            component = "db"
        elif "dns" in error_str:
            component = "dns"
        elif "whois" in error_str:
            component = "whois"
        else:
            component = "unknown"
    
    # Determine severity
    if "critical" in error_str or "fatal" in error_str:
        severity = "critical"
    elif "error" in error_str or error_type in ["ValueError", "TypeError", "KeyError"]:
        severity = "error"
    else:
        severity = "warning"
    
    return {
        "component": component,
        "severity": severity,
        "error_type": error_type,
    }


def track_error(error: Exception, component: Optional[str] = None, severity: Optional[str] = None):
    """
    Track error for metrics and Sentry.
    
    Args:
        error: Exception object
        component: Component name (optional, auto-detected if not provided)
        severity: Severity level (optional, auto-detected if not provided)
    """
    # Categorize error
    categorization = categorize_error(error, component)
    component = categorization["component"]
    severity = severity or categorization["severity"]
    
    # Update metrics
    _error_metrics["total_errors"] += 1
    _error_metrics["errors_by_component"][component] += 1
    _error_metrics["errors_by_severity"][severity] += 1
    
    # Track daily/weekly counts
    today = datetime.utcnow().date().isoformat()
    week = datetime.utcnow().strftime("%Y-W%W")
    _error_metrics["daily_error_count"][today] += 1
    _error_metrics["weekly_error_count"][week] += 1
    
    # Send to Sentry with tags
    if settings.environment in {"production", "staging"}:
        sentry_sdk.set_tag("component", component)
        sentry_sdk.set_tag("severity", severity)
        sentry_sdk.set_tag("error_type", categorization["error_type"])
        sentry_sdk.capture_exception(error)


def get_error_metrics() -> Dict[str, Any]:
    """
    Get error metrics (total errors, errors by component, error trends, etc.).
    
    Returns:
        Dictionary with error metrics
    """
    # Convert defaultdict to regular dict for JSON serialization
    errors_by_component = dict(_error_metrics["errors_by_component"])
    errors_by_severity = dict(_error_metrics["errors_by_severity"])
    daily_error_count = dict(_error_metrics["daily_error_count"])
    weekly_error_count = dict(_error_metrics["weekly_error_count"])
    
    return {
        "total_errors": _error_metrics["total_errors"],
        "errors_by_component": errors_by_component,
        "errors_by_severity": errors_by_severity,
        "daily_error_count": daily_error_count,
        "weekly_error_count": weekly_error_count,
    }


def reset_error_metrics():
    """Reset error metrics (for testing)."""
    global _error_metrics
    _error_metrics = {
        "total_errors": 0,
        "errors_by_component": defaultdict(int),
        "errors_by_severity": defaultdict(int),
        "daily_error_count": defaultdict(int),
        "weekly_error_count": defaultdict(int),
    }

