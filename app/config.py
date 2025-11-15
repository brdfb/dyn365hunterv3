"""Application configuration using Pydantic Settings."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = (
        "postgresql://dyn365hunter:password123@postgres:5432/dyn365hunter"
    )
    db_pool_size: int = 20
    db_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"

    # Environment
    environment: str = "development"
    
    # Error Tracking
    sentry_dsn: Optional[str] = None
    
    # Microsoft SSO (G19)
    azure_client_id: Optional[str] = None
    azure_client_secret: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    azure_redirect_uri: Optional[str] = None
    
    # JWT (G19)
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 90
    
    # Refresh Token Encryption (G19 - Security hardening)
    refresh_token_encryption_key: Optional[str] = None  # Fernet key (base64 encoded)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix="HUNTER_",
    )


# Global settings instance
settings = Settings()
