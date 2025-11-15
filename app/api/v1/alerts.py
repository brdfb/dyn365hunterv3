"""API v1 alerts endpoints - Proxy to legacy handlers."""

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import Optional, List
from app.api.alerts import (
    list_alerts,
    create_alert_config,
    list_alert_configs,
    AlertResponse,
    AlertConfigResponse,
    AlertConfigCreate,
)
from app.db.session import get_db

router = APIRouter(prefix="/alerts", tags=["alerts", "v1"])


@router.get("", response_model=List[AlertResponse])
async def list_alerts_v1(
    domain: Optional[str] = Query(None, description="Filter by domain"),
    alert_type: Optional[str] = Query(None, description="Filter by alert type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, description="Maximum number of alerts to return"),
    request: Request = None,
    db: Session = Depends(get_db),
):
    """V1 endpoint - List alerts with optional filters."""
    return await list_alerts(
        domain=domain,
        alert_type=alert_type,
        status=status,
        limit=limit,
        request=request,
        db=db,
    )


@router.post("/config", response_model=AlertConfigResponse, status_code=201)
async def create_alert_config_v1(
    request_body: AlertConfigCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    """V1 endpoint - Create or update alert configuration."""
    return await create_alert_config(
        request_body=request_body, request=request, db=db
    )


@router.get("/config", response_model=List[AlertConfigResponse])
async def list_alert_configs_v1(request: Request, db: Session = Depends(get_db)):
    """V1 endpoint - List alert configurations for the current user."""
    return await list_alert_configs(request=request, db=db)

