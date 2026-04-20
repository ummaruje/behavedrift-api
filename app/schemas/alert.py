"""Pydantic schemas for alerts."""

from __future__ import annotations
from pydantic import BaseModel, Field


class AlertAcknowledge(BaseModel):
    action_taken: str = Field(..., max_length=500)
    actioned_by: str | None = None


class AlertDismiss(BaseModel):
    reason: str = Field(..., max_length=300)
    dismissed_by: str | None = None
