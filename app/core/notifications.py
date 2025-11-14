"""Notification engine for alerts (G18)."""

from typing import List, Optional
from sqlalchemy.orm import Session
import httpx
import logging
from datetime import datetime
from app.db.models import Alert, AlertConfig
from app.config import settings


logger = logging.getLogger(__name__)


async def send_webhook_notification(webhook_url: str, alert: Alert) -> bool:
    """
    Send webhook notification for an alert.

    Args:
        webhook_url: Webhook URL to send notification to
        alert: Alert object

    Returns:
        True if successful, False otherwise
    """
    try:
        payload = {
            "alert_id": alert.id,
            "domain": alert.domain,
            "alert_type": alert.alert_type,
            "message": alert.alert_message,
            "created_at": alert.created_at.isoformat() if alert.created_at else None,
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(webhook_url, json=payload)
            response.raise_for_status()
            return True

    except Exception as e:
        logger.error(f"Webhook notification failed for alert {alert.id}: {str(e)}")
        return False


async def send_email_notification(email_address: str, alert: Alert) -> bool:
    """
    Send email notification for an alert.

    Args:
        email_address: Email address to send notification to
        alert: Alert object

    Returns:
        True if successful, False otherwise

    Note:
        This is a placeholder. In production, integrate with SMTP service.
    """
    try:
        # TODO: Integrate with SMTP service (SendGrid, AWS SES, etc.)
        logger.info(
            f"Email notification would be sent to {email_address} for alert {alert.id}"
        )
        logger.info(f"Subject: Domain Alert - {alert.domain}")
        logger.info(f"Body: {alert.alert_message}")
        return True

    except Exception as e:
        logger.error(f"Email notification failed for alert {alert.id}: {str(e)}")
        return False


async def process_pending_alerts(db: Session) -> int:
    """
    Process pending alerts and send notifications.

    Args:
        db: Database session

    Returns:
        Number of alerts processed
    """
    # Get pending alerts
    pending_alerts = db.query(Alert).filter(Alert.status == "pending").all()

    if not pending_alerts:
        return 0

    processed = 0

    for alert in pending_alerts:
        # Get alert config for this alert type
        configs = (
            db.query(AlertConfig)
            .filter(
                AlertConfig.alert_type == alert.alert_type, AlertConfig.enabled == True
            )
            .all()
        )

        if not configs:
            # No config, mark as sent (no notification needed)
            alert.status = "sent"
            alert.sent_at = datetime.now()
            processed += 1
            continue

        # Send notifications based on config
        success = False
        for config in configs:
            if config.notification_method == "webhook" and config.webhook_url:
                success = await send_webhook_notification(config.webhook_url, alert)
                if success:
                    alert.notification_method = "webhook"
            elif config.notification_method == "email" and config.email_address:
                success = await send_email_notification(config.email_address, alert)
                if success:
                    alert.notification_method = "email"

        # Update alert status
        if success:
            alert.status = "sent"
            alert.sent_at = datetime.now()
        else:
            alert.status = "failed"

        processed += 1

    db.commit()
    return processed
