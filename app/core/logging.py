"""Structured logging configuration with PII masking."""

import structlog
import logging
import hashlib
from app.config import settings

# Configure structured logging
_processors = [
    structlog.stdlib.filter_by_level,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
]

# Environment-based output format
if settings.environment == "production":
    _processors.append(structlog.processors.JSONRenderer())  # JSON output for production
else:
    _processors.append(structlog.dev.ConsoleRenderer())  # Pretty format for dev

structlog.configure(
    processors=_processors,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Set log level based on environment
log_level = "DEBUG" if settings.environment == "development" else "INFO"
logging.basicConfig(level=getattr(logging, log_level))

# Get logger
logger = structlog.get_logger()


def mask_pii(value: str) -> str:
    """
    Mask PII (email, company_name) - return hash or id.
    
    Args:
        value: PII value to mask
        
    Returns:
        Masked value (hash of the original)
    """
    if not value:
        return ""
    # Return first 8 chars of hash for identification without exposing PII
    return hashlib.sha256(value.encode()).hexdigest()[:8]

