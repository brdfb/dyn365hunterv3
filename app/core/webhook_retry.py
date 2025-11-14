"""Webhook retry logic with exponential backoff."""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.db.models import WebhookRetry


def calculate_next_retry_time(
    retry_count: int, base_delay_seconds: int = 60
) -> datetime:
    """
    Calculate next retry time using exponential backoff.

    Formula: base_delay * (2 ^ retry_count)
    - Retry 1: 60 seconds (1 minute)
    - Retry 2: 120 seconds (2 minutes)
    - Retry 3: 240 seconds (4 minutes)

    Args:
        retry_count: Current retry count (0-indexed)
        base_delay_seconds: Base delay in seconds (default: 60)

    Returns:
        datetime for next retry
    """
    delay_seconds = base_delay_seconds * (2**retry_count)
    return datetime.utcnow() + timedelta(seconds=delay_seconds)


def create_webhook_retry(
    db: Session,
    api_key_id: Optional[int],
    payload: dict,
    domain: Optional[str],
    error_message: Optional[str] = None,
    max_retries: int = 3,
) -> WebhookRetry:
    """
    Create a webhook retry record for failed webhook processing.

    Args:
        db: Database session
        api_key_id: API key ID (optional)
        payload: Original webhook payload
        domain: Extracted domain from payload
        error_message: Error message (optional)
        max_retries: Maximum retries allowed (default: 3)

    Returns:
        WebhookRetry model instance
    """
    retry = WebhookRetry(
        api_key_id=api_key_id,
        payload=payload,
        domain=domain,
        retry_count=0,
        max_retries=max_retries,
        next_retry_at=calculate_next_retry_time(0),
        status="pending",
        error_message=error_message,
    )
    db.add(retry)
    db.commit()
    db.refresh(retry)
    return retry


def retry_webhook(
    db: Session, retry: WebhookRetry, error_message: Optional[str] = None
) -> bool:
    """
    Retry a webhook and update retry record.

    Args:
        db: Database session
        retry: WebhookRetry model instance
        error_message: Error message if retry failed (optional)

    Returns:
        True if retry should continue, False if exhausted
    """
    retry.retry_count += 1
    retry.last_retry_at = datetime.utcnow()

    if retry.retry_count >= retry.max_retries:
        # Exhausted retries
        retry.status = "exhausted"
        retry.error_message = error_message or "Max retries exceeded"
        retry.next_retry_at = None
        db.commit()
        return False

    # Calculate next retry time
    retry.next_retry_at = calculate_next_retry_time(retry.retry_count)
    retry.error_message = error_message
    retry.status = "pending"
    db.commit()
    return True


def mark_webhook_retry_success(db: Session, retry: WebhookRetry):
    """Mark a webhook retry as successful."""
    retry.status = "success"
    retry.last_retry_at = datetime.utcnow()
    retry.next_retry_at = None
    db.commit()


def get_pending_retries(db: Session, limit: int = 100) -> list[WebhookRetry]:
    """
    Get pending webhook retries that are ready to be retried.

    Args:
        db: Database session
        limit: Maximum number of retries to return

    Returns:
        List of WebhookRetry instances ready for retry
    """
    now = datetime.utcnow()
    return (
        db.query(WebhookRetry)
        .filter(WebhookRetry.status == "pending", WebhookRetry.next_retry_at <= now)
        .limit(limit)
        .all()
    )
