"""API v1 scan endpoints - Proxy to legacy handlers."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.scan import (
    scan_domain,
    scan_bulk,
    get_bulk_scan_status,
    get_bulk_scan_results,
    ScanDomainRequest,
    ScanDomainResponse,
    BulkScanRequest,
    BulkScanResponse,
    BulkScanStatusResponse,
)
from app.db.session import get_db

router = APIRouter(prefix="/scan", tags=["scan", "v1"])


@router.post("/domain", response_model=ScanDomainResponse)
async def scan_domain_v1(request: ScanDomainRequest, db: Session = Depends(get_db)):
    """V1 endpoint - Scan a domain for DNS/WHOIS analysis and calculate readiness score."""
    return await scan_domain(request=request, db=db)


@router.post("/bulk", response_model=BulkScanResponse)
async def scan_bulk_v1(request: BulkScanRequest, db: Session = Depends(get_db)):
    """V1 endpoint - Create a bulk scan job for multiple domains."""
    return await scan_bulk(request=request, db=db)


@router.get("/bulk/{job_id}", response_model=BulkScanStatusResponse)
async def get_bulk_scan_status_v1(job_id: str):
    """V1 endpoint - Get bulk scan job status and progress."""
    return await get_bulk_scan_status(job_id=job_id)


@router.get("/bulk/{job_id}/results")
async def get_bulk_scan_results_v1(job_id: str):
    """V1 endpoint - Get bulk scan job results (only for completed jobs)."""
    return await get_bulk_scan_results(job_id=job_id)

