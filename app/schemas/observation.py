"""Pydantic schemas for observations."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field, model_validator


# ---- Signal schemas (mirror OpenAPI spec) ----


class MoodSignal(BaseModel):
    value: int = Field(..., ge=1, le=5)
    scale: str = "1-5"
    notes: str | None = Field(default=None, max_length=300)


class AppetiteSignal(BaseModel):
    value: str = Field(..., pattern="^(excellent|good|fair|poor|refused)$")
    meal: str | None = Field(default=None, pattern="^(breakfast|lunch|dinner|snack)$")
    fluid_intake_ml: int | None = Field(default=None, ge=0)


class SleepSignal(BaseModel):
    value: str = Field(..., pattern="^(good|fair|disturbed|very_disturbed|unknown)$")
    night_wakings: int | None = Field(default=None, ge=0)
    hours_slept: float | None = Field(default=None, ge=0, le=24)


class SocialEngagementSignal(BaseModel):
    value: str = Field(..., pattern="^(engaged|moderate|withdrawn|isolated)$")
    activity_participated: bool | None = None
    activity_name: str | None = None


class PainIndicatorSignal(BaseModel):
    facial_grimacing: bool = False
    guarding: bool = False
    vocalisation: bool = False
    restlessness: bool = False
    verbal_report: bool = False
    painad_score: int | None = Field(default=None, ge=0, le=10)


class MobilitySignal(BaseModel):
    value: str = Field(
        ..., pattern="^(independent|supervised|assisted|dependent|bedbound)$"
    )
    baseline_comparison: str | None = Field(
        default=None,
        pattern="^(better_than_usual|same_as_usual|worse_than_usual|unknown)$",
    )


class AgitationSignal(BaseModel):
    value: str = Field(..., pattern="^(calm|mild|moderate|severe)$")
    type: str | None = Field(
        default=None,
        pattern="^(physical|verbal|wandering|sundowning|other)$",
    )


class ObservationSignals(BaseModel):
    mood: MoodSignal | None = None
    appetite: AppetiteSignal | None = None
    sleep_quality: SleepSignal | None = None
    social_engagement: SocialEngagementSignal | None = None
    pain_indicators: PainIndicatorSignal | None = None
    mobility: MobilitySignal | None = None
    agitation: AgitationSignal | None = None

    @model_validator(mode="after")
    def at_least_one_signal(self) -> "ObservationSignals":
        values = [
            v
            for v in [
                self.mood,
                self.appetite,
                self.sleep_quality,
                self.social_engagement,
                self.pain_indicators,
                self.mobility,
                self.agitation,
            ]
            if v is not None
        ]
        if not values:
            raise ValueError("At least one signal must be provided.")
        return self


class ObservationContext(BaseModel):
    location: str | None = None
    visitor_present: bool | None = None
    medication_administered: bool | None = None
    medication_notes: str | None = Field(default=None, max_length=200)
    staff_id: str | None = None


# ---- Request / Response ----


class ObservationCreate(BaseModel):
    resident_id: str
    observed_at: datetime
    observer_id: str | None = None
    signals: ObservationSignals
    context: ObservationContext | None = None


class DriftEvaluationResult(BaseModel):
    triggered: bool
    drift_score: float
    baseline_status: str
    signals_flagged: list[str]
    alert_generated: dict | None = None
    message: str | None = None


class ObservationResponse(BaseModel):
    observation_id: str
    resident_id: str
    processed_at: datetime
    drift_evaluation: DriftEvaluationResult
    status: str


class ObservationBatchRequest(BaseModel):
    observations: list[ObservationCreate] = Field(..., min_length=1, max_length=100)


class ObservationBatchResponse(BaseModel):
    submitted: int
    processed: int
    failed: int
    results: list[Any]
    errors: list[Any]
