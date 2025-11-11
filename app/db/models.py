"""SQLAlchemy models for Dyn365Hunter MVP."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Boolean, Date, Text, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql import func
from app.db.session import Base


class RawLead(Base):
    """Raw ingested data from CSV, domain input, or webhook."""
    
    __tablename__ = "raw_leads"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False, index=True)  # 'csv', 'domain', 'webhook'
    company_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    domain = Column(String(255), nullable=False, index=True)
    payload = Column(JSONB, nullable=True)  # Additional metadata as JSON
    ingested_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )


class Company(Base):
    """Normalized company information (domain is unique)."""
    
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    canonical_name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=False, unique=True, index=True)  # UNIQUE constraint
    provider = Column(String(50), nullable=True, index=True)  # 'M365', 'Google', 'Yandex', 'Hosting', 'Local', 'Unknown'
    country = Column(String(2), nullable=True)  # ISO 3166-1 alpha-2 country code
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True
    )


class DomainSignal(Base):
    """DNS and WHOIS analysis results for domains."""
    
    __tablename__ = "domain_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(
        String(255),
        ForeignKey("companies.domain", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    spf = Column(Boolean, nullable=True)  # SPF record exists
    dkim = Column(Boolean, nullable=True)  # DKIM record exists
    dmarc_policy = Column(String(50), nullable=True)  # 'none', 'quarantine', 'reject', etc.
    mx_root = Column(String(255), nullable=True, index=True)  # Root domain of MX record
    registrar = Column(String(255), nullable=True)
    expires_at = Column(Date, nullable=True)
    nameservers = Column(ARRAY(Text), nullable=True)  # Array of nameserver hostnames
    scan_status = Column(
        String(50),
        nullable=False,
        default="pending",
        index=True
    )  # 'pending', 'success', 'dns_timeout', 'whois_failed', 'invalid_domain'
    scanned_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )


class LeadScore(Base):
    """Calculated readiness scores and segments for domains."""
    
    __tablename__ = "lead_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(
        String(255),
        ForeignKey("companies.domain", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    readiness_score = Column(Integer, nullable=False, index=True)  # 0-100 score
    segment = Column(String(50), nullable=False, index=True)  # 'Migration', 'Existing', 'Cold', 'Skip'
    reason = Column(Text, nullable=True)  # Human-readable explanation of score/segment
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True
    )

