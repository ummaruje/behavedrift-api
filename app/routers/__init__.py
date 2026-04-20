"""BehaveDrift — Routers package."""

from __future__ import annotations


from app.routers import (
    health,
    residents,
    observations,
    alerts,
    auth,
    webhooks,
    analytics,
)

__all__ = [
    "health",
    "residents",
    "observations",
    "alerts",
    "auth",
    "webhooks",
    "analytics",
]
