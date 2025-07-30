"""Health check endpoints for monitoring the application."""

import logging
import os
import platform
import sys
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.cache.redis_cache import RedisCache, get_redis_cache
from app.core.config.base import settings
from app.db.session import get_db

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["health"])


class ServiceStatus(BaseModel):
    """Service status model."""

    status: str = Field(..., example="ok")
    name: str = Field(..., example="database")
    details: Optional[Dict[str, Any]] = Field(
        None, example={"version": "PostgreSQL 13.3"}
    )
    error: Optional[str] = None
    latency_ms: int = Field(..., example=5)


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., example="ok")
    version: str = Field(..., example="1.0.0")
    timestamp: int = Field(..., example=1634567890)
    uptime: int = Field(..., example=3600)
    environment: str = Field(..., example="production")
    services: List[ServiceStatus] = Field(...)


# Track application start time
_start_time = time.time()


async def check_database(db: Session) -> ServiceStatus:
    """
    Check database connectivity.

    Args:
        db: Database session

    Returns:
        ServiceStatus with database check results
    """
    start_time = time.time()
    service_name = "database"

    try:
        # Execute a simple query to check database connectivity
        result = db.execute(text("SELECT version()")).scalar()

        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)

        return ServiceStatus(
            status="ok",
            name=service_name,
            details={"version": result},
            latency_ms=latency_ms,
        )
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")

        # Calculate latency even for failed requests
        latency_ms = int((time.time() - start_time) * 1000)

        return ServiceStatus(
            status="error", name=service_name, error=str(e), latency_ms=latency_ms
        )


async def check_redis(redis_cache: Optional[RedisCache] = None) -> ServiceStatus:
    """
    Check Redis connectivity.

    Args:
        redis_cache: Redis cache

    Returns:
        ServiceStatus with Redis check results
    """
    start_time = time.time()
    service_name = "redis"

    if redis_cache is None:
        redis_cache = get_redis_cache()

    if redis_cache is None:
        return ServiceStatus(
            status="error",
            name=service_name,
            error="Redis client not available",
            latency_ms=0,
        )

    try:
        # Fix: Don't await the ping result directly since it might be a boolean
        ping_result = redis_cache.client.ping()

        # Check if the result is awaitable (coroutine or has __await__ method)
        if hasattr(ping_result, "__await__"):
            is_connected = await ping_result
        else:
            # If it's already a boolean, use it directly
            is_connected = ping_result

        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)

        if is_connected:
            # Similarly handle info method which might be sync or async
            info_result = redis_cache.client.info()
            if hasattr(info_result, "__await__"):
                info = await info_result
            else:
                info = info_result

            return ServiceStatus(
                status="ok",
                name=service_name,
                details={
                    "version": info.get("redis_version", "unknown"),
                    "used_memory": info.get("used_memory_human", "unknown"),
                    "clients": info.get("connected_clients", "unknown"),
                },
                latency_ms=latency_ms,
            )
        else:
            return ServiceStatus(
                status="error",
                name=service_name,
                error="Failed to connect to Redis",
                latency_ms=latency_ms,
            )
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")

        # Calculate latency even for failed requests
        latency_ms = int((time.time() - start_time) * 1000)

        return ServiceStatus(
            status="error", name=service_name, error=str(e), latency_ms=latency_ms
        )


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    """
    Comprehensive health check endpoint that checks all services.
    """
    services = []

    # Check database
    db_status = await check_database(db)
    services.append(db_status)

    # Check Redis if available
    redis_cache = get_redis_cache()
    redis_status = await check_redis(redis_cache)
    services.append(redis_status)

    # Determine overall status
    overall_status = "ok"
    for service in services:
        if service.status == "error":
            overall_status = "error"
            break

    # Calculate uptime
    uptime = int(time.time() - _start_time)

    return HealthResponse(
        status=overall_status,
        version=settings.VERSION,
        timestamp=int(time.time()),
        uptime=uptime,
        environment=os.getenv("ENVIRONMENT", "development"),
        services=services,
    )


@router.get("/ping")
async def ping():
    """
    Simple ping endpoint for load balancers and basic health checks.
    Returns a simple 200 OK response.
    """
    return {"status": "ok"}


@router.get("/readiness")
async def readiness(db: Session = Depends(get_db)):
    """
    Readiness probe for Kubernetes.
    Checks if the application is ready to receive traffic.
    """
    # Check database connectivity
    db_status = await check_database(db)

    if db_status.status == "error":
        return {
            "status": "not_ready",
            "reason": f"Database check failed: {db_status.error}",
        }

    return {"status": "ready"}


@router.get("/liveness")
async def liveness():
    """
    Liveness probe for Kubernetes.
    Checks if the application is running.
    """
    return {"status": "alive"}


@router.get("/info")
async def info():
    """
    Get application information.
    """
    return {
        "app": {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "uptime": int(time.time() - _start_time),
            "start_time": int(_start_time),
        },
        "system": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
            "memory_info": {
                "virtual_memory": sys.maxsize,
                "pid": os.getpid(),
            },
        },
        "environment": os.getenv("ENVIRONMENT", "development"),
    }
