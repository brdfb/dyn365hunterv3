"""Email generation and validation endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from app.core.email_generator import generate_generic_emails
from app.core.email_validator import validate_email, EmailValidationResult

router = APIRouter(prefix="/email", tags=["email"])


class EmailGenerateRequest(BaseModel):
    """Request model for email generation."""

    domain: str = Field(..., description="Domain name (will be normalized)")


class EmailGenerateResponse(BaseModel):
    """Response model for email generation."""

    domain: str = Field(..., description="Normalized domain name")
    emails: List[str] = Field(
        ..., description="List of generated generic email addresses"
    )


class EmailGenerateAndValidateRequest(BaseModel):
    """Request model for email generation and validation."""

    domain: str = Field(..., description="Domain name (will be normalized)")
    use_smtp: bool = Field(
        False, description="If True, perform SMTP validation (default: False)"
    )


class EmailCheck(BaseModel):
    """Email validation result model."""

    email: str = Field(..., description="Email address")
    status: str = Field(
        ..., description="Validation status: 'valid', 'invalid', or 'unknown'"
    )
    confidence: str = Field(
        ..., description="Confidence level: 'high', 'medium', or 'low'"
    )
    checks: dict = Field(..., description="Validation checks: syntax, mx, smtp")
    reason: Optional[str] = Field(None, description="Reason for the validation result")


class EmailGenerateAndValidateResponse(BaseModel):
    """Response model for email generation and validation."""

    domain: str = Field(..., description="Normalized domain name")
    emails: List[EmailCheck] = Field(
        ..., description="List of generated emails with validation results"
    )


@router.post("/generate", response_model=EmailGenerateResponse, status_code=200)
async def generate_emails(req: EmailGenerateRequest):
    """
    Generate generic email addresses for a domain.

    Generates common generic email addresses (info, sales, admin, etc.)
    for the given domain. Domain will be normalized before generation.

    Args:
        req: Request with domain name

    Returns:
        EmailGenerateResponse with normalized domain and list of generated emails

    Examples:
        >>> POST /email/generate
        >>> {"domain": "example.com"}
        >>> Response: {"domain": "example.com", "emails": ["admin@example.com", ...]}
    """
    domain = req.domain.strip()
    if not domain:
        raise HTTPException(status_code=400, detail="Domain is required")

    # Generate generic emails
    emails = generate_generic_emails(domain)

    if not emails:
        raise HTTPException(
            status_code=400, detail=f"Could not generate emails for domain: {domain}"
        )

    # Normalize domain for response (to show what was actually used)
    from app.core.normalizer import normalize_domain

    normalized_domain = normalize_domain(domain)

    return EmailGenerateResponse(domain=normalized_domain, emails=emails)


@router.post(
    "/generate-and-validate",
    response_model=EmailGenerateAndValidateResponse,
    status_code=200,
)
async def generate_and_validate_emails(req: EmailGenerateAndValidateRequest):
    """
    Generate generic email addresses for a domain and validate them.

    Generates common generic email addresses (info, sales, admin, etc.)
    for the given domain and validates each email address using:
    - Syntax validation (regex)
    - MX record validation (DNS)
    - Optional SMTP validation (if use_smtp=True)

    Args:
        req: Request with domain name and use_smtp flag

    Returns:
        EmailGenerateAndValidateResponse with normalized domain and list of
        generated emails with validation results

    Examples:
        >>> POST /email/generate-and-validate
        >>> {"domain": "example.com", "use_smtp": false}
        >>> Response: {"domain": "example.com", "emails": [{"email": "info@example.com", "status": "valid", ...}]}
    """
    domain = req.domain.strip()
    if not domain:
        raise HTTPException(status_code=400, detail="Domain is required")

    # Generate generic emails
    emails = generate_generic_emails(domain)

    if not emails:
        raise HTTPException(
            status_code=400, detail=f"Could not generate emails for domain: {domain}"
        )

    # Normalize domain for response
    from app.core.normalizer import normalize_domain

    normalized_domain = normalize_domain(domain)

    # Validate each email
    results: List[EmailValidationResult] = [
        validate_email(email, use_smtp=req.use_smtp) for email in emails
    ]

    # Convert to response model
    return EmailGenerateAndValidateResponse(
        domain=normalized_domain,
        emails=[
            EmailCheck(
                email=r.email,
                status=r.status,
                confidence=r.confidence,
                checks=r.checks,
                reason=r.reason,
            )
            for r in results
        ],
    )
