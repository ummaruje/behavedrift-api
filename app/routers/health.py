"""Router: /health — unauthenticated service health check."""

from fastapi import APIRouter
from sqlalchemy import text

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """
    Returns service and dependency health.
    No authentication required — used by load balancers and monitoring tools.
    """
    from app.database import engine
    import redis.asyncio as aioredis
    from app.config import get_settings

    settings = get_settings()
    db_status = "disconnected"
    redis_status = "disconnected"

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        pass

    try:
        r = aioredis.from_url(settings.redis_url, socket_connect_timeout=1)
        await r.ping()
        await r.aclose()
        redis_status = "connected"
    except Exception:
        pass

    overall = "healthy" if db_status == "connected" and redis_status == "connected" else "degraded"

    return {
        "status": overall,
        "version": "1.0.0",
        "database": db_status,
        "redis": redis_status,
    }
