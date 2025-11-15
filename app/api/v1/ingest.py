"""API v1 ingest endpoints - Proxy to legacy handlers."""

from fastapi import APIRouter, Depends, UploadFile, File, Query, BackgroundTasks, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.api.ingest import (
    ingest_domain,
    ingest_csv,
    ingest_webhook,
    DomainIngestRequest,
    DomainIngestResponse,
    WebhookRequest,
    WebhookResponse,
)
from app.db.session import get_db
from app.db.models import ApiKey
from app.core.api_key_auth import verify_api_key

router = APIRouter(prefix="/ingest", tags=["ingest", "v1"])


@router.post("/domain", response_model=DomainIngestResponse, status_code=201)
async def ingest_domain_v1(
    request: DomainIngestRequest, db: Session = Depends(get_db)
):
    """V1 endpoint - Ingest a single domain."""
    return await ingest_domain(request=request, db=db)


@router.post("/csv", status_code=202)
async def ingest_csv_v1(
    file: UploadFile = File(...),
    auto_detect_columns: bool = Query(False, description="Auto-detect column names"),
    auto_scan: bool = Query(False, description="Automatically scan domains after ingestion"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
):
    """V1 endpoint - Ingest domains from CSV or Excel file."""
    return await ingest_csv(
        file=file,
        auto_detect_columns=auto_detect_columns,
        auto_scan=auto_scan,
        background_tasks=background_tasks,
        db=db,
    )


@router.post("/webhook", response_model=WebhookResponse, status_code=201)
async def ingest_webhook_v1(
    request: WebhookRequest,
    api_key: ApiKey = Depends(verify_api_key),
    db: Session = Depends(get_db),
    http_request: Request = None,
):
    """V1 endpoint - Ingest data from webhook with API key authentication."""
    return await ingest_webhook(
        request=request, api_key=api_key, db=db, http_request=http_request
    )

