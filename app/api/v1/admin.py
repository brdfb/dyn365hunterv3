"""API v1 admin endpoints - Proxy to legacy handlers."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.api.admin import (
    create_api_key,
    list_api_keys,
    deactivate_api_key,
    activate_api_key,
    CreateApiKeyRequest,
    ApiKeyResponse,
    ApiKeyListResponse,
)
from app.db.session import get_db

router = APIRouter(prefix="/admin", tags=["admin", "v1"])


@router.post("/api-keys", response_model=ApiKeyResponse, status_code=201)
async def create_api_key_v1(
    request: CreateApiKeyRequest, db: Session = Depends(get_db)
):
    """V1 endpoint - Create a new API key for webhook authentication."""
    return await create_api_key(request=request, db=db)


@router.get("/api-keys", response_model=List[ApiKeyListResponse])
async def list_api_keys_v1(db: Session = Depends(get_db)):
    """V1 endpoint - List all API keys (without showing the actual keys)."""
    return await list_api_keys(db=db)


@router.patch("/api-keys/{key_id}/deactivate")
async def deactivate_api_key_v1(key_id: int, db: Session = Depends(get_db)):
    """V1 endpoint - Deactivate an API key."""
    return await deactivate_api_key(key_id=key_id, db=db)


@router.patch("/api-keys/{key_id}/activate")
async def activate_api_key_v1(key_id: int, db: Session = Depends(get_db)):
    """V1 endpoint - Activate an API key."""
    return await activate_api_key(key_id=key_id, db=db)

