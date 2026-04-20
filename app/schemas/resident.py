"""Pydantic schemas for residents."""

from __future__ import annotations
from datetime import date, datetime
from typing import Any
from pydantic import BaseModel, Field


class ResidentCreate(BaseModel):
    internal_reference: str = Field(..., min_length=1, max_length=255)
    date_of_birth: date | None = None
    diagnosis_codes: list[str] = Field(default_factory=list)
    baseline_window_days: int = Field(default=28, ge=14, le=90)
    risk_profile: str = Field(default="medium", pattern="^(low|medium|high)$")
    notes: str | None = Field(default=None, max_length=500)


class ResidentResponse(BaseModel):
    resident_id: str
    internal_reference: str
    baseline_status: str
    baseline_window_days: int
    risk_profile: str
    diagnosis_codes: list[str]
    total_observations: int
    min_observations_required: int
    created_at: datetime
    last_observation_at: datetime | None = None

    model_config = {"from_attributes": True}


class ResidentList(BaseModel):
    residents: list[ResidentResponse]
    meta: dict[str, Any]


class BaselineSummary(BaseModel):
    resident_id: str
    baseline_status: str
    window_days: int
    window_start: str | None = None
    window_end: str | None = None
    total_observations_in_window: int = 0
    signals: dict[str, Any] = Field(default_factory=dict)
    last_calculated_at: str | None = None


class BaselineReset(BaseModel):
    reason: str = Field(
        ...,
        pattern="^(post_hospitalisation|medication_change|care_plan_change|clinical_review|other)$",
    )
    notes: str | None = Field(default=None, max_length=300)
