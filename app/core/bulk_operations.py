"""Bulk operations optimization utilities (P1-4)."""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.core.redis_client import get_redis_client, is_redis_available


def calculate_optimal_batch_size(
    dns_rate_limit: float = 10.0,  # req/s
    whois_rate_limit: float = 5.0,  # req/s
    batch_duration: float = 10.0,  # seconds
    max_batch_size: int = 100,
) -> int:
    """
    Calculate optimal batch size based on rate limits.

    Each domain requires 1 DNS query + 1 WHOIS query.
    The bottleneck is the slower rate limit (WHOIS: 5 req/s).

    Args:
        dns_rate_limit: DNS rate limit (req/s)
        whois_rate_limit: WHOIS rate limit (req/s)
        batch_duration: Target batch duration (seconds)
        max_batch_size: Maximum batch size (safety limit)

    Returns:
        Optimal batch size
    """
    # Each domain requires 1 DNS + 1 WHOIS query
    # DNS capacity: 10 req/s × 10s = 100 domains
    # WHOIS capacity: 5 req/s × 10s = 50 domains
    # Optimal: min(DNS capacity, WHOIS capacity, max_batch_size)
    dns_capacity = int(dns_rate_limit * batch_duration)
    whois_capacity = int(whois_rate_limit * batch_duration)

    optimal_batch_size = min(dns_capacity, whois_capacity, max_batch_size)

    return optimal_batch_size


def get_partial_commit_log(bulk_id: str) -> Dict:
    """
    Get partial commit log for a bulk scan job.

    Args:
        bulk_id: Bulk scan job ID

    Returns:
        Dictionary with committed and failed domains
    """
    if not is_redis_available():
        return {"committed": [], "failed": []}

    redis_client = get_redis_client()
    if redis_client is None:
        return {"committed": [], "failed": []}

    try:
        log_key = f"bulk_log:{bulk_id}"
        log_data = redis_client.get(log_key)
        if log_data:
            return json.loads(log_data)
    except Exception as e:
        logger.warning("partial_commit_log_get_failed", bulk_id=bulk_id, error=str(e))

    return {"committed": [], "failed": []}


def store_partial_commit_log(
    bulk_id: str,
    batch_no: int,
    total_batches: int,
    committed: List[Dict],
    failed: List[Dict],
) -> bool:
    """
    Store partial commit log for recovery.

    Args:
        bulk_id: Bulk scan job ID
        batch_no: Batch number
        total_batches: Total number of batches
        committed: List of committed domain results
        failed: List of failed domain results

    Returns:
        True if successful, False otherwise
    """
    if not is_redis_available():
        return False

    redis_client = get_redis_client()
    if redis_client is None:
        return False

    try:
        log_key = f"bulk_log:{bulk_id}"
        log_data = {
            "bulk_id": bulk_id,
            "batch_no": batch_no,
            "total_batches": total_batches,
            "committed": committed,
            "failed": failed,
            "batch_start_time": datetime.utcnow().isoformat(),
            "batch_end_time": datetime.utcnow().isoformat(),
        }

        # Store with 24 hour TTL
        redis_client.setex(log_key, 86400, json.dumps(log_data))
        return True
    except Exception as e:
        logger.warning(
            "partial_commit_log_store_failed", bulk_id=bulk_id, error=str(e)
        )
        return False


def get_bulk_log_context(
    bulk_id: str, batch_no: int, total_batches: int, batch_size: int
) -> Dict:
    """
    Get bulk log context for structured logging.

    Args:
        bulk_id: Bulk scan job ID
        batch_no: Batch number
        total_batches: Total number of batches
        batch_size: Batch size

    Returns:
        Dictionary with log context
    """
    return {
        "bulk_id": bulk_id,
        "batch_no": batch_no,
        "total_batches": total_batches,
        "batch_size": batch_size,
    }

