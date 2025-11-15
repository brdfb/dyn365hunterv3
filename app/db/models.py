"""SQLAlchemy models for Dyn365Hunter MVP."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Date,
    Text,
    TIMESTAMP,
    ForeignKey,
    JSON,
)
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql import func
from app.db.session import Base


class RawLead(Base):
    """Raw ingested data from CSV, domain input, or webhook."""

    __tablename__ = "raw_leads"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(
        String(50), nullable=False, index=True
    )  # 'csv', 'domain', 'webhook'
    company_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    domain = Column(String(255), nullable=False, index=True)
    payload = Column(JSONB, nullable=True)  # Additional metadata as JSON
    ingested_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class Company(Base):
    """Normalized company information (domain is unique)."""

    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    canonical_name = Column(String(255), nullable=False)
    domain = Column(
        String(255), nullable=False, unique=True, index=True
    )  # UNIQUE constraint
    provider = Column(
        String(50), nullable=True, index=True
    )  # 'M365', 'Google', 'Yandex', 'Hosting', 'Local', 'Unknown'
    country = Column(String(2), nullable=True)  # ISO 3166-1 alpha-2 country code
    contact_emails = Column(
        JSONB, nullable=True
    )  # Array of contact email addresses (G16: Lead enrichment)
    contact_quality_score = Column(
        Integer, nullable=True, index=True
    )  # Quality score 0-100 (G16: Lead enrichment)
    linkedin_pattern = Column(
        String(255), nullable=True
    )  # Detected LinkedIn email pattern (G16: Lead enrichment)
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True,
    )


class ProviderChangeHistory(Base):
    """History of provider changes for domains."""

    __tablename__ = "provider_change_history"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(
        String(255),
        ForeignKey("companies.domain", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    previous_provider = Column(String(50), nullable=True)  # Previous provider
    new_provider = Column(String(50), nullable=False)  # New provider
    changed_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    scan_id = Column(Integer, nullable=True)  # Reference to domain_signals.id if needed


class DomainSignal(Base):
    """DNS and WHOIS analysis results for domains."""

    __tablename__ = "domain_signals"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(
        String(255),
        ForeignKey("companies.domain", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    spf = Column(Boolean, nullable=True)  # SPF record exists
    dkim = Column(Boolean, nullable=True)  # DKIM record exists
    dmarc_policy = Column(
        String(50), nullable=True
    )  # 'none', 'quarantine', 'reject', etc.
    mx_root = Column(String(255), nullable=True, index=True)  # Root domain of MX record
    registrar = Column(String(255), nullable=True)
    expires_at = Column(Date, nullable=True)
    nameservers = Column(ARRAY(Text), nullable=True)  # Array of nameserver hostnames
    scan_status = Column(
        String(50), nullable=False, default="pending", index=True
    )  # 'pending', 'success', 'dns_timeout', 'whois_failed', 'invalid_domain'
    scanned_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, index=True
    )


class LeadScore(Base):
    """Calculated readiness scores and segments for domains."""

    __tablename__ = "lead_scores"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(
        String(255),
        ForeignKey("companies.domain", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    readiness_score = Column(Integer, nullable=False, index=True)  # 0-100 score
    segment = Column(
        String(50), nullable=False, index=True
    )  # 'Migration', 'Existing', 'Cold', 'Skip'
    reason = Column(Text, nullable=True)  # Human-readable explanation of score/segment
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True,
    )


class ApiKey(Base):
    """API keys for webhook authentication (G16: Webhook infrastructure)."""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_hash = Column(
        String(255), nullable=False, unique=True, index=True
    )  # Hashed API key (SHA-256)
    name = Column(String(255), nullable=False)  # Human-readable name for the key
    rate_limit_per_minute = Column(
        Integer, nullable=False, default=60
    )  # Rate limit per minute per key
    is_active = Column(
        Boolean, nullable=False, default=True, index=True
    )  # Whether the key is active
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    last_used_at = Column(
        TIMESTAMP(timezone=True), nullable=True, index=True
    )  # Last time the key was used
    created_by = Column(String(255), nullable=True)  # Who created the key (admin user)


class WebhookRetry(Base):
    """Failed webhook requests for retry with exponential backoff (G16: Retry logic)."""

    __tablename__ = "webhook_retries"

    id = Column(Integer, primary_key=True, index=True)
    api_key_id = Column(
        Integer,
        ForeignKey("api_keys.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    payload = Column(JSONB, nullable=False)  # Original webhook payload
    domain = Column(
        String(255), nullable=True, index=True
    )  # Extracted domain from payload
    retry_count = Column(
        Integer, nullable=False, default=0
    )  # Number of retries attempted
    max_retries = Column(Integer, nullable=False, default=3)  # Maximum retries allowed
    next_retry_at = Column(
        TIMESTAMP(timezone=True), nullable=True, index=True
    )  # When to retry next (exponential backoff)
    status = Column(
        String(50), nullable=False, default="pending", index=True
    )  # 'pending', 'success', 'failed', 'exhausted'
    error_message = Column(Text, nullable=True)  # Last error message
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    last_retry_at = Column(TIMESTAMP(timezone=True), nullable=True)


class Note(Base):
    """User notes for domains (G17: CRM-lite)."""

    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(
        String(255),
        ForeignKey("companies.domain", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    note = Column(Text, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Tag(Base):
    """Tags for domains with auto-tagging support (G17: CRM-lite)."""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(
        String(255),
        ForeignKey("companies.domain", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tag = Column(String(100), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class Favorite(Base):
    """User favorites for domains, session-based (G17: CRM-lite)."""

    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(
        String(255),
        ForeignKey("companies.domain", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        String(255), nullable=False, index=True
    )  # Session-based user identifier
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class SignalChangeHistory(Base):
    """History of signal changes (SPF, DKIM, DMARC, MX) (G18)."""

    __tablename__ = "signal_change_history"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(
        String(255),
        ForeignKey("companies.domain", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    signal_type = Column(
        String(50), nullable=False, index=True
    )  # 'spf', 'dkim', 'dmarc', 'mx'
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    changed_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, index=True
    )


class ScoreChangeHistory(Base):
    """History of score and segment changes (G18)."""

    __tablename__ = "score_change_history"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(
        String(255),
        ForeignKey("companies.domain", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    old_score = Column(Integer, nullable=True)
    new_score = Column(Integer, nullable=True)
    old_segment = Column(String(50), nullable=True)
    new_segment = Column(String(50), nullable=True)
    changed_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, index=True
    )


class Alert(Base):
    """Generated alerts for domain changes (G18)."""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(
        String(255),
        ForeignKey("companies.domain", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    alert_type = Column(
        String(50), nullable=False, index=True
    )  # 'mx_changed', 'dmarc_added', 'expire_soon', 'score_changed'
    alert_message = Column(Text, nullable=False)
    status = Column(
        String(50), nullable=False, default="pending", index=True
    )  # 'pending', 'sent', 'failed'
    notification_method = Column(
        String(50), nullable=True
    )  # 'email', 'webhook', 'slack'
    sent_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, index=True
    )


class AlertConfig(Base):
    """Alert configuration preferences (G18)."""

    __tablename__ = "alert_config"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        String(255), nullable=False, default="default", index=True
    )  # Session-based user identifier
    alert_type = Column(
        String(50), nullable=False, index=True
    )  # 'mx_changed', 'dmarc_added', 'expire_soon', 'score_changed'
    notification_method = Column(
        String(50), nullable=False
    )  # 'email', 'webhook', 'slack'
    enabled = Column(Boolean, nullable=False, default=True, index=True)
    frequency = Column(
        String(50), nullable=False, default="immediate"
    )  # 'immediate', 'daily_digest'
    webhook_url = Column(Text, nullable=True)  # For webhook notifications
    email_address = Column(String(255), nullable=True)  # For email notifications
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class User(Base):
    """User information from Microsoft SSO (G19)."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    microsoft_id = Column(
        String(255), nullable=False, unique=True, index=True
    )  # Azure AD object ID
    email = Column(String(255), nullable=False, unique=True, index=True)
    display_name = Column(String(255), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    refresh_token_encrypted = Column(
        Text, nullable=True
    )  # Encrypted refresh token (optional, for future use)
    last_login_at = Column(TIMESTAMP(timezone=True), nullable=True, index=True)
    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )