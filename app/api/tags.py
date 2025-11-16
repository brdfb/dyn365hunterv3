"""Tags endpoints for domain tags (G17: CRM-lite).

⚠️ DEPRECATED: Manual tag write endpoints (POST, DELETE) are deprecated as of 2025-11-16.
Read endpoint (GET) remains available for auto-tags (system-generated tags).
Manual tags will be managed in Dynamics 365 in the future.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, Field
from app.db.session import get_db
from app.db.models import Tag, Company
from app.core.normalizer import normalize_domain
from app.core.deprecation import deprecated_endpoint
from app.core.deprecated_monitoring import track_deprecated_endpoint


router = APIRouter(prefix="/leads", tags=["tags"])


class TagCreate(BaseModel):
    """Request model for creating a tag."""

    tag: str = Field(..., description="Tag name", min_length=1, max_length=100)


class TagResponse(BaseModel):
    """Response model for a tag."""

    id: int
    domain: str
    tag: str
    created_at: str

    class Config:
        from_attributes = True


@router.post("/{domain}/tags", status_code=410)
async def create_tag(domain: str, request: TagCreate, db: Session = Depends(get_db)):
    """
    Add a tag to a domain.
    
    ⚠️ DEPRECATED: This endpoint is disabled (410 Gone) as of Phase 3.
    Manual tags are now managed in Dynamics 365. Auto-tags (system-generated) remain available.

    Args:
        domain: Domain name (will be normalized)
        request: Tag creation request
        db: Database session

    Returns:
        410 Gone - Endpoint disabled

    Raises:
        410: Endpoint disabled (read-only mode)
    """
    # Normalize domain for tracking
    normalized_domain = normalize_domain(domain) or domain
    
    # Track deprecated endpoint call
    track_deprecated_endpoint("POST /leads/{domain}/tags", normalized_domain)
    
    # Return 410 Gone
    raise HTTPException(
        status_code=410,
        detail={
            "error": "This endpoint is deprecated and disabled.",
            "reason": "Manual tags are now managed in Dynamics 365. Auto-tags (system-generated) remain available.",
            "alternative": "Use Dynamics 365 Tags API for manual tag management.",
            "migration_guide": "/docs/migration/notes-to-dynamics",
        }
    )


@router.get("/{domain}/tags", response_model=List[TagResponse])
async def list_tags(domain: str, db: Session = Depends(get_db)):
    """
    List all tags for a domain.

    Args:
        domain: Domain name (will be normalized)
        db: Database session

    Returns:
        List of TagResponse objects

    Raises:
        404: If domain not found
        400: If domain is invalid
    """
    # Normalize domain
    normalized_domain = normalize_domain(domain)

    if not normalized_domain:
        raise HTTPException(status_code=400, detail="Invalid domain format")

    # Check if domain exists
    company = db.query(Company).filter(Company.domain == normalized_domain).first()
    if not company:
        raise HTTPException(
            status_code=404,
            detail=f"Domain {normalized_domain} not found. Please ingest the domain first using /ingest/domain",
        )

    # Get tags
    tags = (
        db.query(Tag)
        .filter(Tag.domain == normalized_domain)
        .order_by(Tag.created_at.desc())
        .all()
    )

    return [
        TagResponse(
            id=tag.id,
            domain=tag.domain,
            tag=tag.tag,
            created_at=tag.created_at.isoformat(),
        )
        for tag in tags
    ]


@router.delete("/{domain}/tags/{tag_id}", status_code=410)
async def delete_tag(domain: str, tag_id: int, db: Session = Depends(get_db)):
    """
    Remove a tag from a domain.
    
    ⚠️ DEPRECATED: This endpoint is disabled (410 Gone) as of Phase 3.
    Manual tags are now managed in Dynamics 365. Auto-tags (system-generated) remain available.

    Args:
        domain: Domain name (will be normalized)
        tag_id: Tag ID
        db: Database session

    Returns:
        410 Gone - Endpoint disabled

    Raises:
        410: Endpoint disabled (read-only mode)
    """
    # Normalize domain for tracking
    normalized_domain = normalize_domain(domain) or domain
    
    # Track deprecated endpoint call
    track_deprecated_endpoint("DELETE /leads/{domain}/tags/{tag_id}", normalized_domain)
    
    # Return 410 Gone
    raise HTTPException(
        status_code=410,
        detail={
            "error": "This endpoint is deprecated and disabled.",
            "reason": "Manual tags are now managed in Dynamics 365. Auto-tags (system-generated) remain available.",
            "alternative": "Use Dynamics 365 Tags API for manual tag management.",
            "migration_guide": "/docs/migration/notes-to-dynamics",
        }
    )
