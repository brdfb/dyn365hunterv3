"""Debug endpoints for IP enrichment (internal/admin use only)."""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from app.core.analyzer_enrichment import enrich_ip, check_enrichment_available
from app.core.cache import get_cached_ip_enrichment
from app.core.logging import logger
from app.config import settings
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.db.models import IpEnrichment

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/ip-enrichment/{ip}")
async def debug_ip_enrichment(
    ip: str,
    use_cache: bool = Query(True, description="Use cache for enrichment lookup"),
    db: Session = Depends(get_db),
):
    """
    Debug endpoint for IP enrichment (internal/admin use only).
    
    Returns:
    - Enrichment result from providers (MaxMind, IP2Location, IP2Proxy)
    - Cache status
    - Database record (if exists)
    - Configuration status
    
    Args:
        ip: IP address to enrich
        use_cache: Whether to use cache (default: True)
        db: Database session (optional, for querying stored enrichment)
    """
    result = {
        "ip": ip,
        "enrichment_enabled": settings.enrichment_enabled,
        "config": {
            "maxmind_asn": settings.enrichment_db_path_maxmind_asn,
            "maxmind_city": settings.enrichment_db_path_maxmind_city,
            "ip2location": settings.enrichment_db_path_ip2location,
            "ip2proxy": settings.enrichment_db_path_ip2proxy,
        },
        "availability": {
            "at_least_one_db_available": check_enrichment_available(),
        },
        "cache": {
            "cached": False,
            "cached_result": None,
        },
        "enrichment": {
            "result": None,
            "has_data": False,
        },
        "database": {
            "record_exists": False,
            "record": None,
        },
    }
    
    # Check cache
    if use_cache:
        cached = get_cached_ip_enrichment(ip)
        if cached:
            result["cache"]["cached"] = True
            result["cache"]["cached_result"] = cached
    
    # Perform enrichment (if enabled)
    if settings.enrichment_enabled:
        enrichment_result = enrich_ip(ip, use_cache=use_cache)
        if enrichment_result:
            result["enrichment"]["result"] = enrichment_result.to_dict()
            result["enrichment"]["has_data"] = enrichment_result.has_data()
    
    # Query database (if DB session provided)
    if db:
        try:
            db_record = db.query(IpEnrichment).filter(
                IpEnrichment.ip_address == ip
            ).first()
            if db_record:
                result["database"]["record_exists"] = True
                result["database"]["record"] = {
                    "domain": db_record.domain,
                    "ip_address": db_record.ip_address,
                    "asn": db_record.asn,
                    "asn_org": db_record.asn_org,
                    "isp": db_record.isp,
                    "country": db_record.country,
                    "city": db_record.city,
                    "usage_type": db_record.usage_type,
                    "is_proxy": db_record.is_proxy,
                    "proxy_type": db_record.proxy_type,
                    "created_at": db_record.created_at.isoformat() if db_record.created_at else None,
                    "updated_at": db_record.updated_at.isoformat() if db_record.updated_at else None,
                }
        except Exception as e:
            logger.warning("debug_ip_enrichment_db_query_failed", ip=ip, error=str(e))
            result["database"]["error"] = str(e)
    
    return result


@router.get("/ip-enrichment/config")
async def debug_enrichment_config():
    """
    Debug endpoint for IP enrichment configuration status.
    
    Returns current configuration and availability status.
    """
    return {
        "enrichment_enabled": settings.enrichment_enabled,
        "config": {
            "maxmind_asn": settings.enrichment_db_path_maxmind_asn,
            "maxmind_city": settings.enrichment_db_path_maxmind_city,
            "ip2location": settings.enrichment_db_path_ip2location,
            "ip2proxy": settings.enrichment_db_path_ip2proxy,
        },
        "availability": {
            "at_least_one_db_available": check_enrichment_available(),
        },
        "environment_variable_names": {
            "enabled": "HUNTER_ENRICHMENT_ENABLED",
            "maxmind_asn": "HUNTER_ENRICHMENT_DB_PATH_MAXMIND_ASN",
            "maxmind_city": "HUNTER_ENRICHMENT_DB_PATH_MAXMIND_CITY",
            "ip2location": "HUNTER_ENRICHMENT_DB_PATH_IP2LOCATION",
            "ip2proxy": "HUNTER_ENRICHMENT_DB_PATH_IP2PROXY",
        },
    }

