"""API Key authentication and rate limiting for webhook endpoints."""

import bcrypt
import secrets
from datetime import datetime
from typing import Optional
from fastapi import HTTPException, Security, Depends, Header
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import ApiKey
from app.core.rate_limiter import RateLimiter
from collections import defaultdict
from threading import Lock
import time

# API Key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Per-API-key rate limiters (in-memory, per process)
_api_key_limiters: dict[str, RateLimiter] = {}
_rate_limiter_lock = Lock()


def hash_api_key(api_key: str) -> str:
    """Hash an API key using bcrypt (with salt)."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(api_key.encode(), salt)
    return hashed.decode()


def check_api_key_hash(api_key: str, stored_hash: str) -> bool:
    """Verify API key against stored hash (helper function)."""
    try:
        return bcrypt.checkpw(api_key.encode(), stored_hash.encode())
    except Exception:
        return False


def generate_api_key() -> str:
    """Generate a new API key (32 bytes, base64 encoded)."""
    return secrets.token_urlsafe(32)


def get_api_key_limiter(api_key_id: int, rate_limit_per_minute: int) -> RateLimiter:
    """Get or create a rate limiter for a specific API key."""
    limiter_key = f"api_key_{api_key_id}"

    with _rate_limiter_lock:
        if limiter_key not in _api_key_limiters:
            # Convert per-minute to per-second rate
            rate_per_second = rate_limit_per_minute / 60.0
            _api_key_limiters[limiter_key] = RateLimiter(
                rate=rate_per_second,
                burst=rate_limit_per_minute,  # Allow burst up to per-minute limit
            )
        return _api_key_limiters[limiter_key]


async def verify_api_key(
    x_api_key: Optional[str] = Security(api_key_header), db: Session = Depends(get_db)
) -> ApiKey:
    """
    Verify API key from header and return ApiKey model.

    Args:
        x_api_key: API key from X-API-Key header
        db: Database session

    Returns:
        ApiKey model instance

    Raises:
        HTTPException: If API key is missing, invalid, or inactive
    """
    if not x_api_key:
        raise HTTPException(
            status_code=401, detail="API key required. Please provide X-API-Key header."
        )

    # Look up API key in database (check all active keys)
    # Note: With bcrypt, we can't hash and compare directly, so we need to check each key
    api_keys = db.query(ApiKey).filter(ApiKey.is_active == True).all()
    
    api_key = None
    for key in api_keys:
        if check_api_key_hash(x_api_key, key.key_hash):
            api_key = key
            break

    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")

    # Update last_used_at
    api_key.last_used_at = datetime.utcnow()
    db.commit()

    # Check rate limit
    limiter = get_api_key_limiter(api_key.id, api_key.rate_limit_per_minute)
    if not limiter.acquire():
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Limit: {api_key.rate_limit_per_minute} requests per minute",
        )

    return api_key
