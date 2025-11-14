"""Favorites endpoints for domain favorites (G17: CRM-lite)."""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.db.session import get_db
from app.db.models import Favorite, Company
from app.core.normalizer import normalize_domain
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


@router.post("/{domain}/favorite", response_model=FavoriteResponse, status_code=201)
async def add_favorite(
    domain: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Add a domain to favorites.
    
    Args:
        domain: Domain name (will be normalized)
        request: FastAPI request (for session)
        db: Database session
        
    Returns:
        FavoriteResponse with created favorite
        
    Raises:
        404: If domain not found
        400: If domain is invalid or already favorited
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
            detail=f"Domain {normalized_domain} not found. Please ingest the domain first using /ingest/domain"
        )
    
    # Get user ID from session
    user_id = get_user_id(request)
    
    # Check if already favorited
    existing_favorite = db.query(Favorite).filter(
        Favorite.domain == normalized_domain,
        Favorite.user_id == user_id
    ).first()
    
    if existing_favorite:
        raise HTTPException(
            status_code=400,
            detail=f"Domain {normalized_domain} is already in favorites"
        )
    
    # Create favorite
    favorite = Favorite(
        domain=normalized_domain,
        user_id=user_id
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    
    return FavoriteResponse(
        id=favorite.id,
        domain=favorite.domain,
        user_id=favorite.user_id,
        created_at=favorite.created_at.isoformat()
    )


# Note: GET /leads?favorite=true is handled in leads.py
# This endpoint is kept for backward compatibility but should use leads endpoint


@router.delete("/{domain}/favorite", status_code=204)
async def remove_favorite(
    domain: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Remove a domain from favorites.
    
    Args:
        domain: Domain name (will be normalized)
        request: FastAPI request (for session)
        db: Database session
        
    Raises:
        404: If domain or favorite not found
        400: If domain is invalid
    """
    # Normalize domain
    normalized_domain = normalize_domain(domain)
    
    if not normalized_domain:
        raise HTTPException(status_code=400, detail="Invalid domain format")
    
    # Get user ID from session
    user_id = get_user_id(request)
    
    # Get favorite
    favorite = db.query(Favorite).filter(
        Favorite.domain == normalized_domain,
        Favorite.user_id == user_id
    ).first()
    
    if not favorite:
        raise HTTPException(
            status_code=404,
            detail=f"Domain {normalized_domain} is not in favorites"
        )
    
    # Delete favorite
    db.delete(favorite)
    db.commit()
    
    return None

