"""Alerts endpoints for managing alerts and configurations (G18)."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid
from app.db.session import get_db
from app.db.models import Alert, AlertConfig


router = APIRouter(prefix="/alerts", tags=["alerts"])


def get_user_id(request: Request) -> str:
    """Get user ID from session (session-based, no auth yet)."""
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id


class AlertResponse(BaseModel):
    """Response model for an alert."""

    id: int
    domain: str
    alert_type: str
    alert_message: str
    status: str
    notification_method: Optional[str] = None
    sent_at: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class AlertConfigCreate(BaseModel):
    """Request model for creating alert configuration."""

    alert_type: str = Field(
        ...,
        description="Alert type: mx_changed, dmarc_added, expire_soon, score_changed",
    )
    notification_method: str = Field(
        ..., description="Notification method: email, webhook, slack"
    )
    enabled: bool = Field(True, description="Whether alert is enabled")
    frequency: str = Field(
        "immediate", description="Frequency: immediate, daily_digest"
    )
    webhook_url: Optional[str] = Field(
        None, description="Webhook URL (for webhook notifications)"
    )
    email_address: Optional[str] = Field(
        None, description="Email address (for email notifications)"
    )


class AlertConfigResponse(BaseModel):
    """Response model for alert configuration."""

    id: int
    user_id: str
    alert_type: str
    notification_method: str
    enabled: bool
    frequency: str
    webhook_url: Optional[str] = None
    email_address: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.get("", response_model=List[AlertResponse])
async def list_alerts(
    domain: Optional[str] = None,
    alert_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    request: Request = None,
    db: Session = Depends(get_db),
):
    """
    List alerts with optional filters.

    Query parameters:
    - domain: Filter by domain
    - alert_type: Filter by alert type
    - status: Filter by status (pending, sent, failed)
    - limit: Maximum number of alerts to return (default: 100)

    Returns:
        List of AlertResponse objects
    """
    query = db.query(Alert)

    if domain:
        query = query.filter(Alert.domain == domain)

    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)

    if status:
        query = query.filter(Alert.status == status)

    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()

    return [
        AlertResponse(
            id=alert.id,
            domain=alert.domain,
            alert_type=alert.alert_type,
            alert_message=alert.alert_message,
            status=alert.status,
            notification_method=alert.notification_method,
            sent_at=alert.sent_at.isoformat() if alert.sent_at else None,
            created_at=alert.created_at.isoformat(),
        )
        for alert in alerts
    ]


@router.post("/config", response_model=AlertConfigResponse, status_code=201)
async def create_alert_config(
    request_body: AlertConfigCreate, request: Request, db: Session = Depends(get_db)
):
    """
    Create or update alert configuration.

    Args:
        request_body: Alert configuration data
        request: FastAPI request (for session)
        db: Database session

    Returns:
        AlertConfigResponse with created/updated configuration
    """
    user_id = get_user_id(request)

    # Check if config already exists
    existing = (
        db.query(AlertConfig)
        .filter(
            AlertConfig.user_id == user_id,
            AlertConfig.alert_type == request_body.alert_type,
            AlertConfig.notification_method == request_body.notification_method,
        )
        .first()
    )

    if existing:
        # Update existing config
        existing.enabled = request_body.enabled
        existing.frequency = request_body.frequency
        existing.webhook_url = request_body.webhook_url
        existing.email_address = request_body.email_address
        existing.updated_at = datetime.now()
        db.commit()
        db.refresh(existing)

        return AlertConfigResponse(
            id=existing.id,
            user_id=existing.user_id,
            alert_type=existing.alert_type,
            notification_method=existing.notification_method,
            enabled=existing.enabled,
            frequency=existing.frequency,
            webhook_url=existing.webhook_url,
            email_address=existing.email_address,
            created_at=existing.created_at.isoformat(),
            updated_at=existing.updated_at.isoformat(),
        )
    else:
        # Create new config
        config = AlertConfig(
            user_id=user_id,
            alert_type=request_body.alert_type,
            notification_method=request_body.notification_method,
            enabled=request_body.enabled,
            frequency=request_body.frequency,
            webhook_url=request_body.webhook_url,
            email_address=request_body.email_address,
        )
        db.add(config)
        db.commit()
        db.refresh(config)

        return AlertConfigResponse(
            id=config.id,
            user_id=config.user_id,
            alert_type=config.alert_type,
            notification_method=config.notification_method,
            enabled=config.enabled,
            frequency=config.frequency,
            webhook_url=config.webhook_url,
            email_address=config.email_address,
            created_at=config.created_at.isoformat(),
            updated_at=config.updated_at.isoformat(),
        )


@router.get("/config", response_model=List[AlertConfigResponse])
async def list_alert_configs(request: Request, db: Session = Depends(get_db)):
    """
    List alert configurations for the current user.

    Returns:
        List of AlertConfigResponse objects
    """
    user_id = get_user_id(request)

    configs = db.query(AlertConfig).filter(AlertConfig.user_id == user_id).all()

    return [
        AlertConfigResponse(
            id=config.id,
            user_id=config.user_id,
            alert_type=config.alert_type,
            notification_method=config.notification_method,
            enabled=config.enabled,
            frequency=config.frequency,
            webhook_url=config.webhook_url,
            email_address=config.email_address,
            created_at=config.created_at.isoformat(),
            updated_at=config.updated_at.isoformat(),
        )
        for config in configs
    ]
