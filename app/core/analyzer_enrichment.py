"""IP enrichment utilities using MaxMind, IP2Location, and IP2Proxy databases."""

import os
import threading
from typing import Optional
from dataclasses import dataclass, asdict
from app.config import settings
from app.core.logging import logger
from app.core.cache import get_cached_ip_enrichment, set_cached_ip_enrichment


@dataclass
class IpEnrichmentResult:
    """Normalized IP enrichment result from multiple data sources."""
    
    asn: Optional[int] = None  # Autonomous System Number
    asn_org: Optional[str] = None  # ASN Organization
    isp: Optional[str] = None  # Internet Service Provider
    country: Optional[str] = None  # ISO 3166-1 alpha-2 country code
    city: Optional[str] = None
    usage_type: Optional[str] = None  # DCH, COM, RES, MOB, etc.
    is_proxy: Optional[bool] = None  # Proxy detection result
    proxy_type: Optional[str] = None  # VPN, TOR, PUB, etc.
    
    def to_dict(self) -> dict:
        """Convert to dictionary for caching."""
        return asdict(self)
    
    def has_data(self) -> bool:
        """Check if result contains any enrichment data."""
        return any([
            self.asn is not None,
            self.asn_org is not None,
            self.isp is not None,
            self.country is not None,
            self.city is not None,
            self.usage_type is not None,
            self.is_proxy is not None,
            self.proxy_type is not None,
        ])


# Global readers (lazy-loaded, cached, thread-safe)
# These are process-level singletons (each worker process has its own instance)
_maxmind_asn_reader = None
_maxmind_city_reader = None
_maxmind_country_reader = None
_ip2location_db = None
_ip2proxy_db = None
_loader_lock = threading.Lock()  # Thread safety for lazy loading


def _load_maxmind_asn() -> Optional[object]:
    """Load MaxMind GeoLite2 ASN database reader (thread-safe lazy loading)."""
    global _maxmind_asn_reader
    
    # Fast path: already loaded
    if _maxmind_asn_reader is not None:
        return _maxmind_asn_reader
    
    # Thread-safe lazy loading
    with _loader_lock:
        # Double-check after acquiring lock
        if _maxmind_asn_reader is not None:
            return _maxmind_asn_reader
        
        if not settings.enrichment_db_path_maxmind_asn:
            return None
        
        if not os.path.exists(settings.enrichment_db_path_maxmind_asn):
            logger.warning(
                "maxmind_asn_db_not_found",
                path=settings.enrichment_db_path_maxmind_asn
            )
            return None
        
        try:
            import geoip2.database
            _maxmind_asn_reader = geoip2.database.Reader(settings.enrichment_db_path_maxmind_asn)
            logger.info("maxmind_asn_db_loaded", path=settings.enrichment_db_path_maxmind_asn)
            return _maxmind_asn_reader
        except ImportError:
            logger.warning("maxmind_geoip2_not_installed", hint="pip install geoip2")
            return None
        except Exception as e:
            logger.error("maxmind_asn_db_load_failed", path=settings.enrichment_db_path_maxmind_asn, error=str(e))
            return None


def _load_maxmind_city() -> Optional[object]:
    """Load MaxMind GeoLite2 City database reader (thread-safe lazy loading)."""
    global _maxmind_city_reader
    
    # Fast path: already loaded
    if _maxmind_city_reader is not None:
        return _maxmind_city_reader
    
    # Thread-safe lazy loading
    with _loader_lock:
        # Double-check after acquiring lock
        if _maxmind_city_reader is not None:
            return _maxmind_city_reader
        
        if not settings.enrichment_db_path_maxmind_city:
            return None
        
        if not os.path.exists(settings.enrichment_db_path_maxmind_city):
            logger.warning(
                "maxmind_city_db_not_found",
                path=settings.enrichment_db_path_maxmind_city
            )
            return None
        
        try:
            import geoip2.database
            _maxmind_city_reader = geoip2.database.Reader(settings.enrichment_db_path_maxmind_city)
            logger.info("maxmind_city_db_loaded", path=settings.enrichment_db_path_maxmind_city)
            return _maxmind_city_reader
        except ImportError:
            logger.warning("maxmind_geoip2_not_installed", hint="pip install geoip2")
            return None
        except Exception as e:
            logger.error("maxmind_city_db_load_failed", path=settings.enrichment_db_path_maxmind_city, error=str(e))
            return None


def _load_maxmind_country() -> Optional[object]:
    """Load MaxMind GeoLite2 Country database reader (thread-safe lazy loading, optional fallback)."""
    global _maxmind_country_reader
    
    # Fast path: already loaded
    if _maxmind_country_reader is not None:
        return _maxmind_country_reader
    
    # Thread-safe lazy loading
    with _loader_lock:
        # Double-check after acquiring lock
        if _maxmind_country_reader is not None:
            return _maxmind_country_reader
        
        if not settings.enrichment_db_path_maxmind_country:
            return None
        
        if not os.path.exists(settings.enrichment_db_path_maxmind_country):
            logger.warning(
                "maxmind_country_db_not_found",
                path=settings.enrichment_db_path_maxmind_country
            )
            return None
        
        try:
            import geoip2.database
            _maxmind_country_reader = geoip2.database.Reader(settings.enrichment_db_path_maxmind_country)
            logger.info("maxmind_country_db_loaded", path=settings.enrichment_db_path_maxmind_country)
            return _maxmind_country_reader
        except ImportError:
            logger.warning("maxmind_geoip2_not_installed", hint="pip install geoip2")
            return None
        except Exception as e:
            logger.error("maxmind_country_db_load_failed", path=settings.enrichment_db_path_maxmind_country, error=str(e))
            return None


def _load_ip2location() -> Optional[object]:
    """Load IP2Location LITE database (thread-safe lazy loading)."""
    global _ip2location_db
    
    # Fast path: already loaded
    if _ip2location_db is not None:
        return _ip2location_db
    
    # Thread-safe lazy loading
    with _loader_lock:
        # Double-check after acquiring lock
        if _ip2location_db is not None:
            return _ip2location_db
        
        if not settings.enrichment_db_path_ip2location:
            return None
        
        if not os.path.exists(settings.enrichment_db_path_ip2location):
            logger.warning(
                "ip2location_db_not_found",
                path=settings.enrichment_db_path_ip2location
            )
            return None
        
        try:
            import ip2location
            _ip2location_db = ip2location.IP2Location(settings.enrichment_db_path_ip2location)
            logger.info("ip2location_db_loaded", path=settings.enrichment_db_path_ip2location)
            return _ip2location_db
        except ImportError:
            logger.warning("ip2location_not_installed", hint="pip install ip2location")
            return None
        except Exception as e:
            logger.error("ip2location_db_load_failed", path=settings.enrichment_db_path_ip2location, error=str(e))
            return None


def _load_ip2proxy() -> Optional[object]:
    """Load IP2Proxy LITE database (thread-safe lazy loading)."""
    global _ip2proxy_db
    
    # Fast path: already loaded
    if _ip2proxy_db is not None:
        return _ip2proxy_db
    
    # Thread-safe lazy loading
    with _loader_lock:
        # Double-check after acquiring lock
        if _ip2proxy_db is not None:
            return _ip2proxy_db
        
        if not settings.enrichment_db_path_ip2proxy:
            return None
        
        if not os.path.exists(settings.enrichment_db_path_ip2proxy):
            logger.warning(
                "ip2proxy_db_not_found",
                path=settings.enrichment_db_path_ip2proxy
            )
            return None
        
        try:
            import IP2Proxy
            _ip2proxy_db = IP2Proxy.IP2Proxy()
            _ip2proxy_db.open(settings.enrichment_db_path_ip2proxy)
            logger.info("ip2proxy_db_loaded", path=settings.enrichment_db_path_ip2proxy)
            return _ip2proxy_db
        except ImportError:
            logger.warning("ip2proxy_not_installed", hint="pip install IP2Proxy")
            return None
        except Exception as e:
            logger.error("ip2proxy_db_load_failed", path=settings.enrichment_db_path_ip2proxy, error=str(e))
            return None


def enrich_ip(ip: str, use_cache: bool = True) -> Optional[IpEnrichmentResult]:
    """
    Enrich IP address using MaxMind, IP2Location, and IP2Proxy databases.
    
    Args:
        ip: IP address to enrich (IPv4 or IPv6)
        use_cache: Whether to use cache (default: True)
        
    Returns:
        IpEnrichmentResult with enrichment data, or None if no data sources available
        or all lookups fail
        
    Examples:
        >>> result = enrich_ip("8.8.8.8")
        >>> result.country
        'US'
        >>> result.asn
        15169
    """
    if not ip:
        return None
    
    # Check cache first
    if use_cache:
        cached_result = get_cached_ip_enrichment(ip)
        if cached_result:
            return IpEnrichmentResult(**cached_result)
    
    result = IpEnrichmentResult()
    
    # MaxMind ASN lookup
    try:
        asn_reader = _load_maxmind_asn()
        if asn_reader:
            response = asn_reader.asn(ip)
            result.asn = response.autonomous_system_number
            result.asn_org = response.autonomous_system_organization
    except Exception as e:
        # Graceful fail - log but continue
        logger.debug("maxmind_asn_lookup_failed", ip=ip, error=str(e))
    
    # MaxMind City lookup (includes country data)
    try:
        city_reader = _load_maxmind_city()
        if city_reader:
            response = city_reader.city(ip)
            if response.country.iso_code:
                result.country = response.country.iso_code
            if response.city.name:
                result.city = response.city.name
    except Exception as e:
        # Graceful fail - log but continue
        logger.debug("maxmind_city_lookup_failed", ip=ip, error=str(e))
    
    # MaxMind Country lookup (fallback if City DB not available or country not set)
    if not result.country:
        try:
            country_reader = _load_maxmind_country()
            if country_reader:
                response = country_reader.country(ip)
                if response.country.iso_code:
                    result.country = response.country.iso_code
        except Exception as e:
            # Graceful fail - log but continue
            logger.debug("maxmind_country_lookup_failed", ip=ip, error=str(e))
    
    # IP2Location lookup
    try:
        ip2location_db = _load_ip2location()
        if ip2location_db:
            rec = ip2location_db.get_all(ip)
            if rec:
                if rec.country_short:
                    # Only set if not already set by MaxMind
                    if not result.country:
                        result.country = rec.country_short
                if rec.city:
                    # Only set if not already set by MaxMind
                    if not result.city:
                        result.city = rec.city
                if rec.isp:
                    result.isp = rec.isp
                if rec.usage_type:
                    result.usage_type = rec.usage_type
    except Exception as e:
        # Graceful fail - log but continue
        logger.debug("ip2location_lookup_failed", ip=ip, error=str(e))
    
    # IP2Proxy lookup
    try:
        ip2proxy_db = _load_ip2proxy()
        if ip2proxy_db:
            rec = ip2proxy_db.get_all(ip)
            if rec:
                # is_proxy: "Y" or "N"
                if rec.is_proxy:
                    result.is_proxy = rec.is_proxy == "Y"
                if rec.proxy_type:
                    result.proxy_type = rec.proxy_type
    except Exception as e:
        # Graceful fail - log but continue
        logger.debug("ip2proxy_lookup_failed", ip=ip, error=str(e))
    
    # Return None if no data was collected (all lookups failed or no DBs available)
    if not result.has_data():
        return None
    
    # Cache the result
    if use_cache:
        set_cached_ip_enrichment(ip, result.to_dict())
    
    return result


def check_enrichment_available() -> bool:
    """
    Check if at least one enrichment database is available.
    
    Returns:
        True if at least one DB file exists and is loadable, False otherwise
    """
    # Check if any DB paths are configured
    has_config = any([
        settings.enrichment_db_path_maxmind_asn,
        settings.enrichment_db_path_maxmind_city,
        settings.enrichment_db_path_maxmind_country,
        settings.enrichment_db_path_ip2location,
        settings.enrichment_db_path_ip2proxy,
    ])
    
    if not has_config:
        return False
    
    # Try to load at least one DB
    return any([
        _load_maxmind_asn() is not None,
        _load_maxmind_city() is not None,
        _load_maxmind_country() is not None,
        _load_ip2location() is not None,
        _load_ip2proxy() is not None,
    ])

