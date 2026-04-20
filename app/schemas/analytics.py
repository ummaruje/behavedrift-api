"""Pydantic schemas for analytics endpoints."""
from __future__ import annotations


from datetime import datetime, date
from typing import Any
from pydantic import BaseModel, Field


class ActiveAlertSummary(BaseModel):
    resident_id: str
    tier: str
    primary_signals: list[str]


class RiskDistribution(BaseModel):
    stable: int = 0
    watch_t1: int = 0
    concern_t2: int = 0
    alert_t3: int = 0
    critical_t4: int = 0


class PopulationRiskResponse(BaseModel):
    generated_at: datetime
    location: str | None = None
    total_residents: int
    risk_distribution: RiskDistribution
    trending_signals: list[str] = Field(default_factory=list)
    active_alerts: list[ActiveAlertSummary] = Field(default_factory=list)


class TrendDataPoint(BaseModel):
    date: date
    drift_score: float | None = None
    signals: dict[str, Any] = Field(default_factory=dict)
    alert_tier: str | None = None


class ResidentTrendResponse(BaseModel):
    resident_id: str
    period_start: datetime
    period_end: datetime
    data_points: list[TrendDataPoint] = Field(default_factory=list)
