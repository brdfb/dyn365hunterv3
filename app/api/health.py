"""Health check endpoints for Kubernetes/Docker orchestration."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.config import settings
from app.core.cache import get_cache_metrics
from app.core.distributed_rate_limiter import get_rate_limit_metrics
from app.core.tasks import get_bulk_metrics
from app.core.error_tracking import get_error_metrics
import redis

router = APIRouter(tags=["health"])


# Liveness probe
@router.get("/healthz/live")
async def liveness_probe():
    """
    Liveness probe - indicates the application is running.
    
    Returns:
        200 OK if the application is alive
    """
    return {"status": "alive"}


# Readiness probe
@router.get("/healthz/ready")
async def readiness_probe(db: Session = Depends(get_db)):
    """
    Readiness probe - checks if the application is ready to serve traffic.
    
    Checks:
    - Database connection
    - Redis connection
    
    Returns:
        200 OK if ready, 503 Service Unavailable if not ready
    """
    checks = {}
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception as e:
        checks["database"] = False
        raise HTTPException(
            status_code=503,
            detail=f"Database unavailable: {str(e)}"
        )
    
    # Check Redis (using connection pool from redis_client)
    try:
        from app.core.redis_client import get_redis_client
        redis_client = get_redis_client()
        if redis_client is None:
            checks["redis"] = False
            raise HTTPException(
                status_code=503,
                detail="Redis unavailable: client not initialized"
            )
        redis_client.ping()
        checks["redis"] = True
    except Exception as e:
        checks["redis"] = False
        raise HTTPException(
            status_code=503,
            detail=f"Redis unavailable: {str(e)}"
        )
    
    return {"status": "ready", "checks": checks}


# Startup probe
@router.get("/healthz/startup")
async def startup_probe(db: Session = Depends(get_db)):
    """
    Startup probe - checks if the application has finished starting up.
    
    Returns:
        200 OK if started, 503 Service Unavailable if not ready
    """
    return await readiness_probe(db)


# Legacy endpoint (backward compatibility)
@router.get("/healthz")
async def health_check(db: Session = Depends(get_db)):
    """
    Legacy health check endpoint (backward compatibility).
    
    Returns:
        Status and database connection status (always 200)
    """
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
    
    # Check Redis (non-blocking, using connection pool)
    redis_status = "unknown"
    try:
        from app.core.redis_client import get_redis_client
        redis_client = get_redis_client()
        if redis_client is None:
            redis_status = "disconnected: client not initialized"
        else:
            redis_client.ping()
            redis_status = "connected"
    except Exception as e:
        redis_status = f"disconnected: {str(e)}"

    return {
        "status": "ok",
        "database": db_status,
        "redis": redis_status,
        "environment": settings.environment
    }


@router.get("/healthz/metrics")
async def metrics_endpoint():
    """
    Metrics endpoint - returns cache, rate limit, bulk operations, and error metrics.
    
    Returns:
        Dictionary with all metrics (cache, rate limit, bulk operations, errors)
    """
    try:
        cache_metrics = get_cache_metrics()
        rate_limit_metrics = get_rate_limit_metrics()
        bulk_metrics = get_bulk_metrics()
        error_metrics = get_error_metrics()
        
        return {
            "cache": cache_metrics,
            "rate_limit": rate_limit_metrics,
            "bulk_operations": bulk_metrics,
            "errors": error_metrics,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve metrics: {str(e)}"
        )

