"""Authentication endpoints for Microsoft SSO (G19)."""

import secrets
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.db.models import User
from app.config import settings
from app.core.auth import (
    azure_ad_client,
    jwt_manager,
    get_or_create_user,
    oauth_state_manager,
    refresh_token_encryption,
    TokenRevocationManager,
)
from app.core.favorites_migration import migrate_favorites_from_session
from app.core.logging import logger

router = APIRouter(prefix="/auth", tags=["auth"])

# HTTP Bearer token security
security = HTTPBearer(auto_error=False)


# Request/Response models
class UserResponse(BaseModel):
    """User response model."""

    id: int
    email: str
    display_name: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Token response model."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""

    refresh_token: str


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        User model instance

    Raises:
        HTTPException: If token is invalid or user not found
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = jwt_manager.verify_token(token, token_type="access")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@router.get("/login")
async def login():
    """
    Initiate Microsoft SSO login flow.

    Redirects to Azure AD authorization endpoint.
    """
    if not azure_ad_client.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is not configured",
        )

    # Generate CSRF protection state token
    state = secrets.token_urlsafe(32)

    # Store state in Redis (CSRF protection)
    if not oauth_state_manager.store_state(state):
        logger.warning("Failed to store OAuth state, continuing without state verification")

    # Get authorization URL
    auth_url = azure_ad_client.get_authorization_url(state)

    if not auth_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to generate authorization URL",
        )

    from fastapi.responses import RedirectResponse

    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db),
):
    """
    Handle OAuth callback from Azure AD.

    Args:
        code: Authorization code
        state: CSRF protection state (optional, verification skipped in dev)
        error: Error code from Azure AD
        error_description: Error description
        request: FastAPI request
        db: Database session

    Returns:
        Redirect to frontend with tokens or error
    """
    if error:
        logger.error(
            "OAuth callback error",
            error=error,
            error_description=error_description,
        )
        from fastapi.responses import RedirectResponse

        try:
            if request:
                frontend_url = request.url.scheme + "://" + request.url.hostname
                if request.url.port:
                    frontend_url += f":{request.url.port}"
            else:
                frontend_url = "http://localhost:8000"
        except Exception:
            frontend_url = "http://localhost:8000"
        frontend_url += "/mini-ui/?error=auth_failed"
        return RedirectResponse(url=frontend_url)

    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code not provided",
        )

    # Verify state (CSRF protection)
    if state:
        if not oauth_state_manager.verify_state(state):
            logger.warning("OAuth state verification failed", state=state[:8])
            # In production, this should be a hard failure
            # For development, we allow it but log a warning
            if settings.environment == "production":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid state parameter",
                )

    # Exchange code for tokens
    token_result = azure_ad_client.acquire_token_by_authorization_code(code)

    if not token_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to acquire tokens",
        )

    # Get user info from ID token
    id_token = token_result.get("id_token_claims", {})
    microsoft_id = id_token.get("oid") or id_token.get("sub")
    email = id_token.get("email") or id_token.get("preferred_username")
    display_name = id_token.get("name")
    first_name = id_token.get("given_name")
    last_name = id_token.get("family_name")

    if not microsoft_id or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID token: missing user information",
        )

    # Get or create user
    user = get_or_create_user(
        db=db,
        microsoft_id=microsoft_id,
        email=email,
        display_name=display_name,
        first_name=first_name,
        last_name=last_name,
    )

    # Migrate favorites from session-based to user-based (first login)
    # Get session_id from cookie if available
    session_id = None
    if request:
        session_id = request.cookies.get("session_id")
    
    if session_id:
        is_new_user = user.created_at == user.updated_at  # Rough check for new user
        if is_new_user:
            migrated_count = migrate_favorites_from_session(
                db=db, user=user, session_id=session_id
            )
            if migrated_count > 0:
                logger.info(
                    "Favorites migrated on first login",
                    user_id=user.id,
                    migrated_count=migrated_count,
                )

    # Create JWT tokens
    access_token = jwt_manager.create_access_token(user.id, user.email)
    refresh_token = jwt_manager.create_refresh_token(user.id)

    # Encrypt refresh token before storing (if encryption is enabled)
    encrypted_refresh_token = refresh_token_encryption.encrypt(refresh_token)
    if encrypted_refresh_token:
        refresh_token = encrypted_refresh_token

    # Redirect to frontend with tokens
    from fastapi.responses import RedirectResponse

    try:
        if request:
            frontend_url = request.url.scheme + "://" + request.url.hostname
            if request.url.port:
                frontend_url += f":{request.url.port}"
        else:
            frontend_url = "http://localhost:8000"
    except Exception:
        frontend_url = "http://localhost:8000"
    frontend_url += f"/mini-ui/?access_token={access_token}&refresh_token={refresh_token}"

    return RedirectResponse(url=frontend_url)


@router.post("/logout")
async def logout(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    current_user: User = Depends(get_current_user),
):
    """
    Logout current user and revoke tokens.

    Revokes the current access token and refresh token (if provided).
    """
    # Revoke access token
    if credentials:
        token_id = TokenRevocationManager.get_token_id(credentials.credentials)
        jwt_manager.revocation_manager.revoke_token(token_id)
        logger.info(
            "Access token revoked",
            user_id=current_user.id,
            email=current_user.email,
            token_id=token_id[:8],
        )

    logger.info("User logged out", user_id=current_user.id, email=current_user.email)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information.

    Returns:
        Current user information
    """
    return current_user


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    Refresh access token using refresh token.

    Args:
        request: Refresh token request
        db: Database session

    Returns:
        New access and refresh tokens
    """
    # Decrypt refresh token if encrypted
    refresh_token = refresh_token_encryption.decrypt(request.refresh_token)
    if not refresh_token:
        refresh_token = request.refresh_token  # Fallback to plaintext

    # Verify refresh token
    payload = jwt_manager.verify_token(refresh_token, token_type="refresh")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Revoke old refresh token (token rotation)
    old_token_id = TokenRevocationManager.get_token_id(refresh_token)
    jwt_manager.revocation_manager.revoke_token(old_token_id)

    # Create new tokens
    access_token = jwt_manager.create_access_token(user.id, user.email)
    new_refresh_token = jwt_manager.create_refresh_token(user.id)

    # Encrypt new refresh token
    encrypted_refresh_token = refresh_token_encryption.encrypt(new_refresh_token)
    if encrypted_refresh_token:
        new_refresh_token = encrypted_refresh_token

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            first_name=user.first_name,
            last_name=user.last_name,
        ),
    )

