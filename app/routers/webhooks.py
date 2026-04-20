"""Router: /v1/webhooks — webhook endpoint registration and management."""
from __future__ import annotations


import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth.dependencies import get_current_tenant
from app.database import get_db
from app.exceptions import NotFoundError, ValidationError
from app.models.webhook import Webhook
from app.models.tenant import Tenant
from app.schemas.webhook import WebhookCreate, WebhookResponse, VALID_WEBHOOK_EVENTS

router = APIRouter(prefix="/v1/webhooks", tags=["Webhooks"])


@router.post("", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    payload: WebhookCreate,
    tenant: Annotated[Tenant, Depends(get_current_tenant)],
    db: AsyncSession = Depends(get_db),
):
    """
    Register a webhook endpoint to receive BehaveDrift events.

    All events are signed with HMAC-SHA256 using the returned `signing_secret`.
    **The signing_secret is shown only once — store it immediately.**
    """
    # Validate event names
    invalid_events = [e for e in payload.events if e not in VALID_WEBHOOK_EVENTS]
    if invalid_events:
        raise ValidationError(
            f"Invalid event types: {', '.join(invalid_events)}. "
            f"Valid events: {', '.join(VALID_WEBHOOK_EVENTS)}"
        )

    # Generate signing secret
    signing_secret_plain = f"whsec_{secrets.token_hex(16)}"

    webhook = Webhook(
        tenant_id=tenant.id,
        url=payload.url,
        events=payload.events,
        description=payload.description,
        active=payload.active,
        min_tier=payload.min_tier,
        signing_secret=signing_secret_plain,
    )
    db.add(webhook)
    await db.flush()

    return {
        "webhook_id": webhook.id,
        "url": webhook.url,
        "events": webhook.events,
        "active": webhook.active,
        "signing_secret": signing_secret_plain,
        "created_at": webhook.created_at,
        "last_triggered_at": webhook.last_triggered_at,
    }


@router.get("")
async def list_webhooks(
    tenant: Annotated[Tenant, Depends(get_current_tenant)],
    db: AsyncSession = Depends(get_db),
):
    """List all registered webhooks for the authenticated tenant."""
    result = await db.execute(select(Webhook).where(Webhook.tenant_id == tenant.id))
    webhooks = result.scalars().all()

    return {
        "webhooks": [
            {
                "webhook_id": wh.id,
                "url": wh.url,
                "events": wh.events,
                "active": wh.active,
                "signing_secret": None,  # Never returned after creation
                "created_at": wh.created_at,
                "last_triggered_at": wh.last_triggered_at,
            }
            for wh in webhooks
        ]
    }


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: str,
    tenant: Annotated[Tenant, Depends(get_current_tenant)],
    db: AsyncSession = Depends(get_db),
):
    """Remove a registered webhook."""
    result = await db.execute(
        select(Webhook).where(
            Webhook.id == webhook_id,
            Webhook.tenant_id == tenant.id,
        )
    )
    webhook = result.scalar_one_or_none()
    if not webhook:
        raise NotFoundError(f"Webhook '{webhook_id}' not found.")

    await db.delete(webhook)
    await db.flush()
