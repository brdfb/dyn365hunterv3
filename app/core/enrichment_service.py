"""IP enrichment service with separate DB session for safe fire-and-forget operations."""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import desc
from app.db.session import SessionLocal
from app.db.models import IpEnrichment
from app.config import settings
from app.core.analyzer_enrichment import enrich_ip, IpEnrichmentResult, check_enrichment_available
from app.core.logging import logger


def save_ip_enrichment(domain: str, ip: str, result: IpEnrichmentResult, db: Session) -> None:
    """
    Save IP enrichment result to database (UPSERT).
    
    Uses PostgreSQL's INSERT ... ON CONFLICT DO UPDATE for atomic UPSERT.
    
    Args:
        domain: Domain name
        ip: IP address
        result: Enrichment result
        db: Database session
    """
    # Prepare data for insert
    enrichment_data = {
        "domain": domain,
        "ip_address": ip,
        "asn": result.asn,
        "asn_org": result.asn_org,
        "isp": result.isp,
        "country": result.country,
        "city": result.city,
        "usage_type": result.usage_type,
        "is_proxy": result.is_proxy,
        "proxy_type": result.proxy_type,
    }
    
    # PostgreSQL UPSERT using INSERT ... ON CONFLICT
    stmt = insert(IpEnrichment).values(**enrichment_data)
    stmt = stmt.on_conflict_do_update(
        index_elements=["domain", "ip_address"],
        set_={
            "asn": stmt.excluded.asn,
            "asn_org": stmt.excluded.asn_org,
            "isp": stmt.excluded.isp,
            "country": stmt.excluded.country,
            "city": stmt.excluded.city,
            "usage_type": stmt.excluded.usage_type,
            "is_proxy": stmt.excluded.is_proxy,
            "proxy_type": stmt.excluded.proxy_type,
            "updated_at": stmt.excluded.updated_at,
        }
    )
    
    db.execute(stmt)
    db.commit()


def enrich_domain_if_enabled(domain: str, ip: str, db: Session) -> Optional[IpEnrichmentResult]:
    """
    Enrich domain IP if enrichment is enabled and IP is available.
    
    This function:
    1. Checks if enrichment is enabled
    2. Validates IP address
    3. Checks cache first
    4. Performs enrichment if needed
    5. Saves to database
    
    Args:
        domain: Domain name
        ip: IP address to enrich
        db: Database session
        
    Returns:
        Enrichment result if successful, None otherwise
    """
    if not settings.enrichment_enabled:
        return None
    
    if not ip:
        logger.debug("ip_enrichment_skipped", domain=domain, reason="no_ip")
        return None
    
    # Safety check: ensure at least one DB is available
    if not check_enrichment_available():
        logger.warning(
            "ip_enrichment_skipped",
            domain=domain,
            reason="no_db_files_available",
            hint="Check HUNTER_ENRICHMENT_DB_PATH_* environment variables"
        )
        return None
    
    # Perform enrichment (cache is handled inside enrich_ip)
    result = enrich_ip(ip, use_cache=True)
    if not result:
        logger.debug("ip_enrichment_no_data", domain=domain, ip=ip)
        return None
    
    # Save to database
    try:
        save_ip_enrichment(domain, ip, result, db)
        logger.info("ip_enrichment_saved", domain=domain, ip=ip)
    except Exception as e:
        logger.error("ip_enrichment_save_failed", domain=domain, ip=ip, error=str(e), exc_info=True)
        # Tag Sentry event for enrichment errors
        try:
            import sentry_sdk
            sentry_sdk.set_tag("hunter_enrichment_error", "true")
        except ImportError:
            pass  # Sentry not available
        raise
    
    return result


def spawn_enrichment(domain: str, ip: str) -> None:
    """
    Spawn IP enrichment in a separate DB session (fire-and-forget).
    
    This function creates a new database session to ensure enrichment
    failures don't affect the main scan transaction.
    
    Args:
        domain: Domain name
        ip: IP address to enrich
    """
    if not settings.enrichment_enabled:
        return
    
    if not ip:
        return
    
    # Create new session for enrichment
    db = SessionLocal()
    try:
        enrich_domain_if_enabled(domain, ip, db)
    except Exception as e:
        # Log error but don't raise - this is fire-and-forget
        logger.warning(
            "ip_enrichment_failed",
            domain=domain,
            ip=ip,
            error=str(e),
            exc_info=True
        )
        # Tag Sentry event for enrichment errors
        try:
            import sentry_sdk
            sentry_sdk.set_tag("hunter_enrichment_error", "true")
        except ImportError:
            pass  # Sentry not available
        db.rollback()
    finally:
        db.close()


def latest_ip_enrichment(domain: str, db: Session) -> Optional[IpEnrichment]:
    """
    Get the most recent IP enrichment record for a domain.
    
    Args:
        domain: Domain name
        db: Database session
        
    Returns:
        Most recent IpEnrichment record, or None if not found
    """
    return (
        db.query(IpEnrichment)
        .filter(IpEnrichment.domain == domain)
        .order_by(desc(IpEnrichment.updated_at))
        .first()
    )


def build_infra_summary(domain: str, db: Session) -> Optional[str]:
    """
    Build a human-readable infrastructure summary from IP enrichment data.
    
    Format: "Hosted on {UsageType}, ISP: {ISP}, Country: {Country}"
    
    Args:
        domain: Domain name
        db: Database session
        
    Returns:
        Infrastructure summary string, or None if no enrichment data available
    """
    record = latest_ip_enrichment(domain, db)
    if not record:
        return None
    
    # Map usage type codes to human-readable names
    usage_type_map = {
        "DCH": "DataCenter",
        "COM": "Commercial",
        "RES": "Residential",
        "MOB": "Mobile",
    }
    
    parts = []
    
    # Usage type (most important signal)
    if record.usage_type:
        usage_name = usage_type_map.get(record.usage_type, record.usage_type)
        parts.append(f"Hosted on {usage_name}")
    
    # ISP (if available)
    if record.isp:
        parts.append(f"ISP: {record.isp}")
    
    # Country (if available)
    if record.country:
        parts.append(f"Country: {record.country}")
    
    # Return None if no data available
    if not parts:
        return None
    
    return ", ".join(parts)

