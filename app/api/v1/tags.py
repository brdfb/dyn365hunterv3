"""API v1 tags endpoints - Proxy to legacy handlers."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.api.tags import create_tag, list_tags, delete_tag, TagCreate, TagResponse
from app.db.session import get_db

router = APIRouter(prefix="/leads", tags=["tags", "v1"])


@router.post("/{domain}/tags", response_model=TagResponse, status_code=201)
async def create_tag_v1(domain: str, request: TagCreate, db: Session = Depends(get_db)):
    """V1 endpoint - Add a tag to a domain."""
    return await create_tag(domain=domain, request=request, db=db)


@router.get("/{domain}/tags", response_model=List[TagResponse])
async def list_tags_v1(domain: str, db: Session = Depends(get_db)):
    """V1 endpoint - List all tags for a domain."""
    return await list_tags(domain=domain, db=db)


@router.delete("/{domain}/tags/{tag_id}", status_code=204)
async def delete_tag_v1(domain: str, tag_id: int, db: Session = Depends(get_db)):
    """V1 endpoint - Remove a tag from a domain."""
    return await delete_tag(domain=domain, tag_id=tag_id, db=db)

