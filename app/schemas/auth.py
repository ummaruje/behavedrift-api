"""Pydantic schemas for authentication and tenant provisioning."""
from __future__ import annotations


from pydantic import BaseModel, Field


class TokenRequest(BaseModel):
    grant_type: str = Field(..., pattern="^client_credentials$")
    client_id: str = Field(..., min_length=1)
    client_secret: str = Field(..., min_length=1)
    scope: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    scope: str


class TenantCreate(BaseModel):
    organisation_name: str = Field(..., min_length=1, max_length=255)
    contact_email: str = Field(..., min_length=1, max_length=255)
    plan: str = Field(
        default="self_hosted", pattern="^(self_hosted|starter|enterprise)$"
    )


class TenantResponse(BaseModel):
    tenant_id: str
    organisation_name: str
    client_id: str
    client_secret: str
    api_key: str
    message: str = (
        "Store the client_secret and api_key securely — they will not be shown again."
    )
