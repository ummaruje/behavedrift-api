"""
BehaveDrift API — FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config import get_settings
from app.exceptions import (
    BehaveDriftError,
    behavedrift_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
)
from app.middleware.logging import RequestIDMiddleware, setup_logging
from app.middleware.rate_limit import RateLimitMiddleware
from app.redis import init_redis, close_redis
from app.routers import health, residents, observations, alerts, auth, webhooks, analytics

settings = get_settings()


# ============================================================
# Lifespan — startup / shutdown
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup tasks before yielding, then cleanup on shutdown."""
    # Startup
    import structlog
    setup_logging()
    
    import logging
    logging.basicConfig(level=settings.log_level)
    log = structlog.get_logger("behavedrift")
    log.info(f"Starting BehaveDrift API v1.0.0 [{settings.app_env}]")

    # Connect to Redis
    await init_redis(settings.redis_url)

    yield

    # Shutdown
    await close_redis()
    
    from app.database import engine
    await engine.dispose()
    log.info("BehaveDrift API shut down cleanly.")


# ============================================================
# App instance
# ============================================================

app = FastAPI(
    title="BehaveDrift API",
    version="1.0.0",
    description=(
        "Open-source AI inference engine for behavioural pattern drift detection "
        "in dementia residents. Integrates with Nourish, Radar Healthcare, and "
        "any FHIR R4-compatible care platform."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ============================================================
# Middleware (outermost first)
# ============================================================

# Request ID injection — must come before everything else
app.add_middleware(RequestIDMiddleware)

# Rate Limiting
app.add_middleware(RateLimitMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security: Only allow configured hosts
if settings.is_production:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts,
    )


# ============================================================
# Exception handlers
# ============================================================

app.add_exception_handler(BehaveDriftError, behavedrift_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


# ============================================================
# Routers
# ============================================================

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(residents.router)
app.include_router(observations.router)
app.include_router(alerts.router)
app.include_router(webhooks.router)
app.include_router(analytics.router)
