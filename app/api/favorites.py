"""Favorites endpoints for domain favorites (G17: CRM-lite).

⚠️ DEPRECATED: Write endpoints (POST, DELETE) are deprecated as of 2025-11-16.
Read endpoint (GET /leads?favorite=true) remains available for migration support.
Favorites will be managed in Dynamics 365 in the future.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.db.session import get_db
from app.db.models import Favorite, Company
from app.core.normalizer import normalize_domain
from app.core.deprecation import deprecated_endpoint
from app.core.deprecated_monitoring import track_deprecated_endpoint
import uuid


router = APIRouter(prefix="/leads", tags=["favorites"])


def get_user_id(request: Request) -> str:
    """
    Get user ID from session (session-based, no auth yet).

    For now, we use a session cookie or generate a default user_id.
    In the future, this will be replaced with proper authentication.
    """
    # Try to get session ID from cookie
    session_id = request.cookies.get("session_id")

    if not session_id:
        # Generate a new session ID (for demo purposes)
        # In production, this should be handled by proper session management
        session_id = str(uuid.uuid4())

    return session_id


class FavoriteResponse(BaseModel):
    """Response model for a favorite."""

    id: int
    domain: str
    user_id: str
    created_at: str

    class Config:
        from_attributes = True


@router.post("/{domain}/favorite", status_code=410)
async def add_favorite(domain: str, request: Request, db: Session = Depends(get_db)):
    """
    Add a domain to favorites.
    
    ⚠️ DEPRECATED: This endpoint is disabled (410 Gone) as of Phase 3.
    Favorites are now managed in Dynamics 365.

    Args:
        domain: Domain name (will be normalized)
        request: FastAPI request (for session)
        db: Database session

    Returns:
        410 Gone - Endpoint disabled

    Raises:
        410: Endpoint disabled (read-only mode)
    """
    # Normalize domain for tracking
    normalized_domain = normalize_domain(domain) or domain
    
    # Track deprecated endpoint call
    track_deprecated_endpoint("POST /leads/{domain}/favorite", normalized_domain)
    
    # Return 410 Gone
    raise HTTPException(
        status_code=410,
        detail={
            "error": "This endpoint is deprecated and disabled.",
            "reason": "Favorites are now managed in Dynamics 365.",
            "alternative": "Use Dynamics 365 Favorite field for favorite management.",
            "migration_guide": "/docs/migration/notes-to-dynamics",
        }
    )


# Note: GET /leads?favorite=true is handled in leads.py
# This endpoint is kept for backward compatibility but should use leads endpoint


@router.delete("/{domain}/favorite", status_code=410)
async def remove_favorite(domain: str, request: Request, db: Session = Depends(get_db)):
    """
    Remove a domain from favorites.
    
    ⚠️ DEPRECATED: This endpoint is disabled (410 Gone) as of Phase 3.
    Favorites are now managed in Dynamics 365.

    Args:
        domain: Domain name (will be normalized)
        request: FastAPI request (for session)
        db: Database session

    Returns:
        410 Gone - Endpoint disabled

    Raises:
        410: Endpoint disabled (read-only mode)
    """
    # Normalize domain for tracking
    normalized_domain = normalize_domain(domain) or domain
    
    # Track deprecated endpoint call
    track_deprecated_endpoint("DELETE /leads/{domain}/favorite", normalized_domain)
    
    # Return 410 Gone
    raise HTTPException(
        status_code=410,
        detail={
            "error": "This endpoint is deprecated and disabled.",
            "reason": "Favorites are now managed in Dynamics 365.",
            "alternative": "Use Dynamics 365 Favorite field for favorite management.",
            "migration_guide": "/docs/migration/notes-to-dynamics",
        }
    )
