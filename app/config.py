"""Application configuration using Pydantic Settings."""

from typing import Optional
from pydantic import Field, AliasChoices
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
    
    # Sales Engine (Phase 2)
    sales_engine_opportunity_factor: float = 1.0  # Tuning factor for opportunity potential (0.0-2.0, default: 1.0)
    
    # IP Enrichment (Feature flag: disabled by default)
    enrichment_enabled: bool = False
    # MaxMind databases - support both new (MAXMIND_*) and old (HUNTER_ENRICHMENT_DB_PATH_MAXMIND_*) env var names
    enrichment_db_path_maxmind_asn: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("MAXMIND_ASN_DB", "HUNTER_ENRICHMENT_DB_PATH_MAXMIND_ASN")
    )  # Path to GeoLite2-ASN.mmdb (optional)
    enrichment_db_path_maxmind_city: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("MAXMIND_CITY_DB", "HUNTER_ENRICHMENT_DB_PATH_MAXMIND_CITY")
    )  # Path to GeoLite2-City.mmdb
    enrichment_db_path_maxmind_country: Optional[str] = Field(
        default=None,
        validation_alias="MAXMIND_COUNTRY_DB"
    )  # Path to GeoLite2-Country.mmdb (optional, fallback for country-only lookups)
    # IP2Location & IP2Proxy - support both new (IP2*_DB) and old (HUNTER_ENRICHMENT_DB_PATH_IP2*) env var names
    enrichment_db_path_ip2location: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("IP2LOCATION_DB", "HUNTER_ENRICHMENT_DB_PATH_IP2LOCATION")
    )  # Path to IP2LOCATION-LITE-DB11.BIN
    enrichment_db_path_ip2proxy: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("IP2PROXY_DB", "HUNTER_ENRICHMENT_DB_PATH_IP2PROXY")
    )  # Path to IP2PROXY-LITE-PX11.BIN

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix="HUNTER_",
    )


# Global settings instance
settings = Settings()
