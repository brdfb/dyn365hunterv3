"""API v1 rescan endpoints - Proxy to legacy handlers."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.api.rescan import (
    rescan_single_domain,
    bulk_rescan,
    RescanDomainResponse,
)
from app.db.session import get_db

router = APIRouter(prefix="/scan", tags=["rescan", "v1"])


@router.post("/{domain}/rescan", response_model=RescanDomainResponse)
async def rescan_single_domain_v1(domain: str, db: Session = Depends(get_db)):
    """V1 endpoint - Re-scan a single domain and detect changes."""
    return await rescan_single_domain(domain=domain, db=db)


@router.post("/bulk/rescan")
async def bulk_rescan_v1(
    domain_list: Optional[str] = Query(
        None, description="Comma-separated list of domains"
    ),
    db: Session = Depends(get_db),
):
    """V1 endpoint - Bulk rescan multiple domains."""
    return await bulk_rescan(domain_list=domain_list, db=db)

