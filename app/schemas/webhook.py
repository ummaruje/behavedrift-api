"""Pydantic schemas for webhooks."""

from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field


VALID_WEBHOOK_EVENTS = [
    "alert.created",
    "alert.tier_escalated",
    "alert.acknowledged",
    "alert.resolved",
    "baseline.updated",
    "resident.risk_status_changed",
]


class WebhookCreate(BaseModel):
    url: str = Field(..., min_length=1, max_length=1024)
    events: list[str] = Field(..., min_length=1)
    description: str | None = Field(default=None, max_length=200)
    active: bool = True
    min_tier: str = Field(default="T1", pattern="^(T1|T2|T3|T4)$")


class WebhookResponse(BaseModel):
    webhook_id: str
    url: str
    events: list[str]
    active: bool
    signing_secret: str | None = None  # Returned only on creation
    created_at: datetime
    last_triggered_at: datetime | None = None
