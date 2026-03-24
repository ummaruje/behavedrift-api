"""Router: /v1/auth — OAuth2 token issuance and tenant provisioning."""

import secrets
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth.hashing import hash_secret, verify_secret
from app.auth.jwt import create_access_token
from app.config import get_settings
from app.database import get_db
from app.exceptions import InvalidCredentialsError, ConflictError, ValidationError
from app.models.tenant import Tenant
from app.schemas.auth import TokenResponse, TenantCreate, TenantResponse

settings = get_settings()
router = APIRouter(prefix="/v1/auth", tags=["Auth"])


# ---- Token issuance (OAuth2 Client Credentials) ----

@router.post("/token", response_model=TokenResponse)
async def issue_token(
    grant_type: Annotated[str, Form()],
    client_id: Annotated[str, Form()],
    client_secret: Annotated[str, Form()],
    scope: Annotated[str | None, Form()] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Exchange client credentials for a short-lived JWT access token (60 min).

    Accepts application/x-www-form-urlencoded as per OAuth2 spec.
    """
    if grant_type != "client_credentials":
        raise ValidationError("Only grant_type='client_credentials' is supported.")

    # Look up tenant by client_id
    result = await db.execute(
        select(Tenant).where(
            Tenant.client_id == client_id,
            Tenant.is_active == True,  # noqa: E712
        )
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise InvalidCredentialsError("client_id or client_secret is incorrect.")

    # Verify client_secret
    if not verify_secret(client_secret, tenant.client_secret_hash):
        raise InvalidCredentialsError("client_id or client_secret is incorrect.")

    # Determine granted scopes
    requested_scopes = scope.split() if scope else ["behavedrift:read", "behavedrift:write"]
    granted_scopes = requested_scopes

    # Issue JWT
    token = create_access_token(
        subject=client_id,
        tenant_id=tenant.id,
        scopes=granted_scopes,
    )

    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
        "scope": " ".join(granted_scopes),
    }


# ---- Tenant provisioning ----

@router.post("/tenants", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    payload: TenantCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Provision a new tenant organisation.

    Returns client_id, client_secret, and api_key.
    **These secrets are shown only once — store them immediately.**
    """
    # Check uniqueness
    existing = await db.execute(
        select(Tenant).where(Tenant.organisation_name == payload.organisation_name)
    )
    if existing.scalar_one_or_none():
        raise ConflictError(
            f"Organisation '{payload.organisation_name}' is already registered."
        )

    # Generate credentials
    tenant_id = f"ten_{uuid.uuid4().hex[:8]}"
    client_id = f"{tenant_id}_client"
    client_secret_plain = f"cs_{secrets.token_hex(20)}"
    api_key_plain = f"bda_sk_{secrets.token_hex(20)}"

    tenant = Tenant(
        id=tenant_id,
        organisation_name=payload.organisation_name,
        contact_email=payload.contact_email,
        plan=payload.plan,
        client_id=client_id,
        client_secret_hash=hash_secret(client_secret_plain),
        api_key_hash=hash_secret(api_key_plain),
    )
    db.add(tenant)
    await db.flush()

    return {
        "tenant_id": tenant.id,
        "organisation_name": tenant.organisation_name,
        "client_id": client_id,
        "client_secret": client_secret_plain,
        "api_key": api_key_plain,
        "message": "Store the client_secret and api_key securely — they will not be shown again.",
    }
