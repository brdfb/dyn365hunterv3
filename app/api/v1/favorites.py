"""API v1 favorites endpoints - Proxy to legacy handlers."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.api.favorites import add_favorite, remove_favorite, FavoriteResponse
from app.db.session import get_db

router = APIRouter(prefix="/leads", tags=["favorites", "v1"])


@router.post("/{domain}/favorite", response_model=FavoriteResponse, status_code=201)
async def add_favorite_v1(domain: str, request: Request, db: Session = Depends(get_db)):
    """V1 endpoint - Add a domain to favorites."""
    return await add_favorite(domain=domain, request=request, db=db)


@router.delete("/{domain}/favorite", status_code=204)
async def remove_favorite_v1(domain: str, request: Request, db: Session = Depends(get_db)):
    """V1 endpoint - Remove a domain from favorites."""
    return await remove_favorite(domain=domain, request=request, db=db)

