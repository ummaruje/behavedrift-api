"""
FastAPI auth dependencies — injected into route handlers.

Supports:
  - Bearer JWT tokens (OAuth2 Client Credentials)
  - API Key via X-API-Key header

All auth is tenant-scoped. A valid token always resolves to a Tenant.
"""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth.jwt import verify_token
from app.auth.hashing import verify_secret
from app.config import get_settings
from app.database import get_db
from app.exceptions import AuthenticationError, ForbiddenError
from app.models.tenant import Tenant
import structlog

settings = get_settings()
_bearer_scheme = HTTPBearer(auto_error=False)


async def _get_tenant_by_token(
    credentials: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> Tenant | None:
    """Attempt to authenticate via Bearer JWT."""
    if not credentials:
        return None
    try:
        payload = verify_token(credentials.credentials)
        tenant_id = payload["tenant_id"]
    except AuthenticationError:
        return None

    result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id, Tenant.is_active == True)  # noqa: E712
    )
    return result.scalar_one_or_none()


async def _get_tenant_by_api_key(
    x_api_key: str | None,
    db: AsyncSession,
) -> Tenant | None:
    """Attempt to authenticate via API Key header."""
    if not x_api_key or len(x_api_key) < settings.api_key_min_length:
        return None

    # Fetch all active tenants with an API key set — then verify hash
    # In production, prefix lookup (first 8 chars) reduces DB scan
    result = await db.execute(
        select(Tenant).where(
            Tenant.is_active == True,  # noqa: E712
            Tenant.api_key_hash.isnot(None),
        )
    )
    tenants = result.scalars().all()
    for tenant in tenants:
        if tenant.api_key_hash and verify_secret(x_api_key, tenant.api_key_hash):
            return tenant
    return None


async def get_current_tenant(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    db: AsyncSession = Depends(get_db),
) -> Tenant:
    """
    FastAPI dependency — resolves the current authenticated tenant.
    Raises 401 if neither JWT nor API Key is valid.
    """
    tenant = await _get_tenant_by_token(credentials, db)
    if not tenant:
        tenant = await _get_tenant_by_api_key(x_api_key, db)
    if not tenant:
        raise AuthenticationError("A valid Bearer token or X-API-Key header is required.")
        
    structlog.contextvars.bind_contextvars(tenant_id=tenant.id)
    return tenant


def require_scope(scope: str):
    """
    Dependency factory — verifies the current token includes a specific scope.
    Only applies to JWT tokens (API Keys get full access within tenant).
    """
    def _check(
        credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
        tenant: Annotated[Tenant, Depends(get_current_tenant)],
    ) -> Tenant:
        if credentials:
            from app.auth.jwt import verify_token
            payload = verify_token(credentials.credentials)
            granted_scopes = payload.get("scopes", [])
            if scope not in granted_scopes:
                raise ForbiddenError(
                    f"This action requires scope '{scope}'. "
                    f"Your token has: {', '.join(granted_scopes)}"
                )
        # API key auth — full access within tenant
        return tenant

    return _check
