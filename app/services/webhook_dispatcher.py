"""
Webhook Dispatch Service 
Handles firing webhook payloads to registered endpoints.
"""

import httpx
import hmac
import hashlib
import json
import asyncio
from datetime import datetime, timezone
from typing import Any, Dict
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.webhook import Webhook
from app.config import get_settings
import ulid

settings = get_settings()

import structlog
logger = structlog.get_logger("behavedrift.webhooks")

def generate_signature(payload_bytes: bytes, secret: str) -> str:
    """Generate HMAC-SHA256 signature for webhook payload."""
    signature = hmac.new(
        key=secret.encode("utf-8"),
        msg=payload_bytes,
        digestmod=hashlib.sha256
    ).hexdigest()
    return signature

async def dispatch_webhook_event(tenant_id: str, event_type: str, data: Dict[str, Any]):
    """
    Fire-and-forget background task to dispatch an event to all matched webhooks for a tenant.
    """
    async with AsyncSessionLocal() as session:
        stmt = select(Webhook).where(
            Webhook.tenant_id == tenant_id,
            Webhook.active == True
        )
        result = await session.execute(stmt)
        webhooks = result.scalars().all()
        
    matched_webhooks = [
        w for w in webhooks 
        if event_type in w.events or "*" in w.events
    ]
    
    if not matched_webhooks:
        return

    event_id = f"evt_{ulid.new().str.lower()}"
    timestamp = datetime.now(timezone.utc).isoformat()
    
    payload = {
        "event_id": event_id,
        "event_type": event_type,
        "tenant_id": tenant_id,
        "timestamp": timestamp,
        "data": data
    }
    
    payload_bytes = json.dumps(payload).encode("utf-8")

    async with httpx.AsyncClient(timeout=settings.webhook_timeout_seconds) as client:
        # Run all requests concurrently
        tasks = []
        for webhook in matched_webhooks:
            signature = generate_signature(payload_bytes, webhook.signing_secret)
            headers = {
                "Content-Type": "application/json",
                "BehaveDrift-Signature": signature,
                "BehaveDrift-Event-ID": event_id,
                "BehaveDrift-Event-Type": event_type,
            }
            tasks.append(
                _send_with_retry(client, webhook, payload_bytes, headers)
            )
            
        await asyncio.gather(*tasks, return_exceptions=True)

async def _send_with_retry(client: httpx.AsyncClient, webhook: Webhook, payload_bytes: bytes, headers: dict):
    """Attempt to send the webhook, obeying retry rules from settings."""
    for attempt in range(1, settings.webhook_retry_attempts + 1):
        try:
            response = await client.post(webhook.url, content=payload_bytes, headers=headers)
            if response.is_success:
                logger.info(
                    "Webhook delivered successfully",
                    webhook_id=webhook.id,
                    url=webhook.url,
                    status=response.status_code
                )
                
                # Update last_triggered_at (requires new session)
                async with AsyncSessionLocal() as session:
                    stmt = select(Webhook).where(Webhook.id == webhook.id)
                    result = await session.execute(stmt)
                    w = result.scalar_one_or_none()
                    if w:
                        w.last_triggered_at = datetime.now(timezone.utc)
                        await session.commit()
                        
                return True
                
            logger.warning(
                "Webhook delivery failed",
                webhook_id=webhook.id,
                status=response.status_code,
                attempt=attempt
            )
        except httpx.RequestError as exc:
            logger.warning(
                "Webhook request error",
                webhook_id=webhook.id,
                error=str(exc),
                attempt=attempt
            )
            
        if attempt < settings.webhook_retry_attempts:
            await asyncio.sleep(settings.webhook_retry_backoff_seconds)
            
    logger.error("Webhook permanently failed after retries", webhook_id=webhook.id)
    return False
