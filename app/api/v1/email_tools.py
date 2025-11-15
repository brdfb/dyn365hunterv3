"""API v1 email tools endpoints - Proxy to legacy handlers."""

from fastapi import APIRouter, Query
from typing import Optional
from app.api.email_tools import (
    generate_emails,
    generate_and_validate_emails,
    EmailGenerateRequest,
    EmailGenerateResponse,
    EmailGenerateAndValidateRequest,
    EmailGenerateAndValidateResponse,
)

router = APIRouter(prefix="/email", tags=["email", "v1"])


@router.post("/generate", response_model=EmailGenerateResponse, status_code=200)
async def generate_emails_v1(req: EmailGenerateRequest):
    """V1 endpoint - Generate generic email addresses for a domain."""
    return await generate_emails(req=req)


@router.post(
    "/generate-and-validate", response_model=EmailGenerateAndValidateResponse, status_code=200
)
async def generate_and_validate_emails_v1(
    req: EmailGenerateAndValidateRequest,
    use_smtp: Optional[bool] = Query(False, description="Enable SMTP validation"),
):
    """V1 endpoint - Generate and validate email addresses for a domain."""
    return await generate_and_validate_emails(req=req, use_smtp=use_smtp)

