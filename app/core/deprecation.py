"""Deprecation decorator for G21 Architecture Refactor.

Marks endpoints as deprecated with warnings and response headers.
"""

from functools import wraps
from datetime import datetime
from typing import Callable, Any
from fastapi import Response
from fastapi.responses import JSONResponse
import json
from app.core.logging import logger

# Deprecation dates
DEPRECATION_DATE = datetime(2025, 11, 16)  # Phase 1 start date
REMOVAL_DATE = datetime(2026, 2, 1)  # ~75 days later (Phase 6 cleanup)


def deprecated_endpoint(
    reason: str,
    alternative: str,
    removal_date: datetime = REMOVAL_DATE,
):
    """
    Mark endpoint as deprecated with warning.
    
    Args:
        reason: Reason for deprecation
        alternative: Alternative endpoint or service to use
        removal_date: Date when endpoint will be removed
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Log deprecation warning
            logger.warning(
                "deprecated_endpoint_called",
                endpoint=func.__name__,
                reason=reason,
                alternative=alternative,
                removal_date=removal_date.isoformat(),
            )
            
            # Call original function
            response = await func(*args, **kwargs)
            
            # Add deprecation headers to response
            # FastAPI endpoints can return various types: Pydantic models, dicts, Response objects, etc.
            if isinstance(response, (JSONResponse, Response)):
                # Already a Response object - add headers directly
                response.headers["X-Deprecated"] = "true"
                response.headers["X-Deprecation-Reason"] = reason
                response.headers["X-Alternative"] = alternative
                response.headers["X-Removal-Date"] = removal_date.isoformat()
                response.headers["X-Deprecation-Date"] = DEPRECATION_DATE.isoformat()
                return response
            elif response is None:
                # 204 No Content - create Response with headers
                return Response(
                    status_code=204,
                    headers={
                        "X-Deprecated": "true",
                        "X-Deprecation-Reason": reason,
                        "X-Alternative": alternative,
                        "X-Removal-Date": removal_date.isoformat(),
                        "X-Deprecation-Date": DEPRECATION_DATE.isoformat(),
                    }
                )
            else:
                # Pydantic model or dict - wrap in JSONResponse with headers
                if hasattr(response, "model_dump"):
                    # Pydantic v2
                    content = response.model_dump()
                elif hasattr(response, "dict"):
                    # Pydantic v1
                    content = response.dict()
                elif isinstance(response, dict):
                    content = response
                else:
                    # Other types - try to serialize
                    content = response
                
                return JSONResponse(
                    content=content,
                    headers={
                        "X-Deprecated": "true",
                        "X-Deprecation-Reason": reason,
                        "X-Alternative": alternative,
                        "X-Removal-Date": removal_date.isoformat(),
                        "X-Deprecation-Date": DEPRECATION_DATE.isoformat(),
                    }
                )
        return wrapper
    return decorator

