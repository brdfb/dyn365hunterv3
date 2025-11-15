"""Microsoft SSO authentication and JWT token handling (G19)."""

import msal
import redis
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
from app.config import settings
from app.db.models import User
from app.core.logging import logger


class AzureADClient:
    """Microsoft Azure AD OAuth 2.0 client."""

    def __init__(self):
        """Initialize Azure AD client."""
        if not all(
            [
                settings.azure_client_id,
                settings.azure_client_secret,
                settings.azure_tenant_id,
            ]
        ):
            logger.warning(
                "Azure AD credentials not configured. Authentication will be disabled."
            )
            self.enabled = False
            return

        self.enabled = True
        self.client_id = settings.azure_client_id
        self.client_secret = settings.azure_client_secret
        self.tenant_id = settings.azure_tenant_id
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.redirect_uri = settings.azure_redirect_uri or "http://localhost:8000/auth/callback"
        # MSAL: openid is automatically added, don't include it explicitly
        # User.Read is Microsoft Graph API scope
        # Note: openid scope is reserved and automatically included by MSAL
        self.scopes = ["User.Read"]

        # Create MSAL app
        self.app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=self.authority,
        )

    def get_authorization_url(self, state: str) -> Optional[str]:
        """
        Get Azure AD authorization URL.

        Args:
            state: CSRF protection state token

        Returns:
            Authorization URL or None if disabled
        """
        if not self.enabled:
            return None

        auth_url = self.app.get_authorization_request_url(
            scopes=self.scopes,
            redirect_uri=self.redirect_uri,
            state=state,
        )
        return auth_url

    def acquire_token_by_authorization_code(
        self, code: str
    ) -> Optional[Dict[str, Any]]:
        """
        Exchange authorization code for tokens.

        Args:
            code: Authorization code from callback

        Returns:
            Token response or None if failed
        """
        if not self.enabled:
            return None

        try:
            result = self.app.acquire_token_by_authorization_code(
                code=code,
                scopes=self.scopes,
                redirect_uri=self.redirect_uri,
            )

            if "error" in result:
                logger.error("Token acquisition failed", error=result.get("error"))
                return None

            return result
        except Exception as e:
            logger.error("Token acquisition exception", error=str(e))
            return None


class OAuthStateManager:
    """OAuth state/nonce storage in Redis (CSRF protection)."""

    def __init__(self):
        """Initialize OAuth state manager."""
        try:
            self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
            self.state_prefix = "oauth_state:"
            self.state_ttl = 600  # 10 minutes
        except Exception as e:
            logger.warning("Redis not available for OAuth state storage", error=str(e))
            self.redis_client = None

    def store_state(self, state: str) -> bool:
        """
        Store OAuth state in Redis.

        Args:
            state: OAuth state token

        Returns:
            True if stored successfully, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            key = f"{self.state_prefix}{state}"
            self.redis_client.setex(key, self.state_ttl, "1")
            return True
        except Exception as e:
            logger.error("Failed to store OAuth state", error=str(e))
            return False

    def verify_state(self, state: str) -> bool:
        """
        Verify OAuth state exists in Redis.

        Args:
            state: OAuth state token

        Returns:
            True if state exists, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            key = f"{self.state_prefix}{state}"
            exists = self.redis_client.exists(key)
            if exists:
                # Delete state after verification (one-time use)
                self.redis_client.delete(key)
            return bool(exists)
        except Exception as e:
            logger.error("Failed to verify OAuth state", error=str(e))
            return False


class TokenRevocationManager:
    """Token revocation management."""

    def __init__(self):
        """Initialize token revocation manager."""
        try:
            self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
            self.revoked_prefix = "revoked_token:"
            # Revoked tokens stored with TTL matching refresh token expiry (90 days)
            self.revoked_ttl = settings.jwt_refresh_token_expire_days * 24 * 3600
        except Exception as e:
            logger.warning("Redis not available for token revocation", error=str(e))
            self.redis_client = None

    def revoke_token(self, token_id: str) -> bool:
        """
        Revoke a token by storing its ID in Redis.

        Args:
            token_id: Token ID (hash of token)

        Returns:
            True if revoked successfully, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            key = f"{self.revoked_prefix}{token_id}"
            self.redis_client.setex(key, self.revoked_ttl, "1")
            return True
        except Exception as e:
            logger.error("Failed to revoke token", error=str(e))
            return False

    def is_revoked(self, token_id: str) -> bool:
        """
        Check if a token is revoked.

        Args:
            token_id: Token ID (hash of token)

        Returns:
            True if revoked, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            key = f"{self.revoked_prefix}{token_id}"
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error("Failed to check token revocation", error=str(e))
            return False

    @staticmethod
    def get_token_id(token: str) -> str:
        """
        Get token ID (hash) for revocation tracking.

        Args:
            token: JWT token

        Returns:
            Token ID (SHA-256 hash)
        """
        return hashlib.sha256(token.encode()).hexdigest()


class RefreshTokenEncryption:
    """Refresh token encryption using Fernet."""

    def __init__(self):
        """Initialize refresh token encryption."""
        if settings.refresh_token_encryption_key:
            try:
                self.fernet = Fernet(settings.refresh_token_encryption_key.encode())
            except Exception as e:
                logger.warning("Invalid refresh token encryption key", error=str(e))
                self.fernet = None
        else:
            # Generate a key if not provided (development only)
            if settings.environment == "development":
                logger.warning("Refresh token encryption key not set, generating temporary key")
                key = Fernet.generate_key()
                self.fernet = Fernet(key)
            else:
                logger.error("Refresh token encryption key required in production")
                self.fernet = None

    def encrypt(self, token: str) -> Optional[str]:
        """
        Encrypt refresh token.

        Args:
            token: Refresh token

        Returns:
            Encrypted token or None if encryption failed
        """
        if not self.fernet:
            return token  # Return plaintext if encryption not available

        try:
            return self.fernet.encrypt(token.encode()).decode()
        except Exception as e:
            logger.error("Failed to encrypt refresh token", error=str(e))
            return None

    def decrypt(self, encrypted_token: str) -> Optional[str]:
        """
        Decrypt refresh token.

        Args:
            encrypted_token: Encrypted refresh token

        Returns:
            Decrypted token or None if decryption failed
        """
        if not self.fernet:
            return encrypted_token  # Return as-is if encryption not available

        try:
            return self.fernet.decrypt(encrypted_token.encode()).decode()
        except Exception as e:
            logger.error("Failed to decrypt refresh token", error=str(e))
            return None


class JWTManager:
    """JWT token generation and validation."""

    def __init__(self):
        """Initialize JWT manager."""
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.jwt_access_token_expire_minutes
        self.refresh_token_expire_days = settings.jwt_refresh_token_expire_days
        self.revocation_manager = TokenRevocationManager()

    def create_access_token(self, user_id: int, email: str) -> str:
        """
        Create JWT access token.

        Args:
            user_id: User ID
            email: User email

        Returns:
            JWT access token
        """
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self.access_token_expire_minutes
        )
        payload = {
            "sub": str(user_id),
            "email": email,
            "exp": expire,
            "type": "access",
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: int) -> str:
        """
        Create JWT refresh token.

        Args:
            user_id: User ID

        Returns:
            JWT refresh token
        """
        expire = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "type": "refresh",
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token
            token_type: Token type ('access' or 'refresh')

        Returns:
            Decoded payload or None if invalid
        """
        try:
            # Check if token is revoked
            token_id = TokenRevocationManager.get_token_id(token)
            if self.revocation_manager.is_revoked(token_id):
                logger.debug("Token is revoked", token_id=token_id[:8])
                return None

            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != token_type:
                return None
            return payload
        except JWTError as e:
            logger.debug("JWT verification failed", error=str(e))
            return None


def get_or_create_user(
    db: Session, microsoft_id: str, email: str, display_name: Optional[str] = None,
    first_name: Optional[str] = None, last_name: Optional[str] = None
) -> User:
    """
    Get or create user from Microsoft SSO data.

    Args:
        db: Database session
        microsoft_id: Azure AD object ID
        email: User email
        display_name: Display name
        first_name: First name
        last_name: Last name

    Returns:
        User model instance
    """
    user = db.query(User).filter(User.microsoft_id == microsoft_id).first()

    if user:
        # Update user info
        user.email = email
        user.display_name = display_name
        user.first_name = first_name
        user.last_name = last_name
        user.last_login_at = datetime.now(timezone.utc)
        user.updated_at = datetime.now(timezone.utc)
    else:
        # Create new user
        user = User(
            microsoft_id=microsoft_id,
            email=email,
            display_name=display_name,
            first_name=first_name,
            last_name=last_name,
            last_login_at=datetime.now(timezone.utc),
        )
        db.add(user)

    db.commit()
    db.refresh(user)
    return user


# Global instances
azure_ad_client = AzureADClient()
jwt_manager = JWTManager()
oauth_state_manager = OAuthStateManager()
refresh_token_encryption = RefreshTokenEncryption()

