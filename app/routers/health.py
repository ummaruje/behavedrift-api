"""Router: /health — unauthenticated service health check."""

from __future__ import annotations


from fastapi import APIRouter
from sqlalchemy import text

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """
    Returns service and dependency health.
    No authentication required — used by load balancers and monitoring tools.

    Core status is determined by database connectivity alone.
    Redis is optional (used for rate limiting only) and reported separately.
    """
    from app.database import engine
    from app import redis as redis_module

    db_status = "disconnected"
    redis_status = "not configured"

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        pass

    # Report Redis status based on whether it was initialised at startup
    if redis_module.redis_client is not None:
        try:
            await redis_module.redis_client.ping()
            redis_status = "connected"
        except Exception:
            redis_status = "disconnected"

    # Core health is based on database only — Redis is optional infrastructure
    overall = "healthy" if db_status == "connected" else "unhealthy"

    return {
        "status": overall,
        "version": "1.0.0",
        "database": db_status,
        "redis": redis_status,
    }
