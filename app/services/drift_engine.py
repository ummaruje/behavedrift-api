"""
BehaveDrift Drift Engine — Core detection service.

Algorithm:
  For each signal in an observation, compute a z-score against the resident's
  baseline (mean ± std_dev). Aggregate flagged signals into a composite drift
  score using a weighted average, then classify into tiers T1–T4.

  Where the baseline is still initialising (< min_observations), scoring is
  skipped and observations are simply accumulated.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.config import get_settings
from app.patterns.infection_patterns import match_clinical_pattern

settings = get_settings()

# Z-score threshold at which a single signal is considered "flagged"
_SIGNAL_Z_FLAG_THRESHOLD = 2.0

# Weights for each signal type — clinical significance
_SIGNAL_WEIGHTS: dict[str, float] = {
    "mood": 1.2,
    "appetite": 1.0,
    "sleep_quality": 1.1,
    "social_engagement": 0.9,
    "pain_indicators": 1.5,
    "mobility": 1.3,
    "agitation": 1.2,
}

# Ordinal signal mappings (string → numeric for z-score)
_APPETITE_MAP = {"excellent": 5, "good": 4, "fair": 3, "poor": 2, "refused": 1}
_SLEEP_MAP = {
    "good": 4,
    "fair": 3,
    "disturbed": 2,
    "very_disturbed": 1,
    "unknown": None,
}
_SOCIAL_MAP = {"engaged": 4, "moderate": 3, "withdrawn": 2, "isolated": 1}
_MOBILITY_MAP = {
    "independent": 5,
    "supervised": 4,
    "assisted": 3,
    "dependent": 2,
    "bedbound": 1,
}
_AGITATION_MAP = {"calm": 1, "mild": 2, "moderate": 3, "severe": 4}


def _signal_to_numeric(signal_name: str, signal_data: dict[str, Any]) -> float | None:
    """Convert a signal dict to a single numeric value for z-scoring."""
    if signal_name == "mood":
        return float(signal_data.get("value", 0))

    if signal_name == "appetite":
        raw = signal_data.get("value")
        return float(_APPETITE_MAP.get(raw, 0)) if raw else None

    if signal_name == "sleep_quality":
        raw = signal_data.get("value")
        return float(v) if (v := _SLEEP_MAP.get(raw)) is not None else None  # type: ignore[arg-type]

    if signal_name == "social_engagement":
        raw = signal_data.get("value")
        return float(_SOCIAL_MAP.get(raw, 0)) if raw else None

    if signal_name == "pain_indicators":
        # Score = count of True flags (0–5)
        flags = [
            "facial_grimacing",
            "guarding",
            "vocalisation",
            "restlessness",
            "verbal_report",
        ]
        return float(sum(1 for f in flags if signal_data.get(f, False)))

    if signal_name == "mobility":
        raw = signal_data.get("value")
        return float(_MOBILITY_MAP.get(raw, 0)) if raw else None

    if signal_name == "agitation":
        raw = signal_data.get("value")
        return float(_AGITATION_MAP.get(raw, 1)) if raw else None

    return None


def _z_score(value: float, mean: float, std: float) -> float:
    """Compute z-score. Returns 0.0 if std is zero (no variance in baseline)."""
    if std < 1e-6:
        # If baseline has no variance, check absolute deviation
        return abs(value - mean) * 5.0
    return abs(value - mean) / std


@dataclass
class SignalEvaluation:
    signal: str
    current_value: float
    baseline_mean: float
    baseline_std: float
    z_score: float
    flagged: bool


@dataclass
class DriftEvaluation:
    drift_score: float
    triggered: bool
    tier: str | None
    tier_label: str | None
    confidence_score: float
    signals_flagged: list[str]
    signal_details: list[SignalEvaluation] = field(default_factory=list)
    clinical_pattern: dict | None = None
    message: str | None = None


def evaluate_drift(
    signals: dict[str, Any],
    baseline_data: dict[str, Any],
    risk_profile: str = "medium",
) -> DriftEvaluation:
    """
    Core drift evaluation function.

    Args:
        signals: Raw signal dict from the incoming observation.
        baseline_data: The resident's current baseline statistics.
        risk_profile: Sensitivity adjustment (low/medium/high).

    Returns:
        A DriftEvaluation containing score, tier, and signal breakdown.
    """
    if not baseline_data:
        return DriftEvaluation(
            drift_score=0.0,
            triggered=False,
            tier=None,
            tier_label=None,
            confidence_score=0.0,
            signals_flagged=[],
            message="Baseline is still initialising — observation recorded for accumulation.",
        )

    baseline_signals: dict[str, dict] = baseline_data.get("signals", {})
    evaluations: list[SignalEvaluation] = []

    for signal_name, signal_data in signals.items():
        if signal_name not in baseline_signals:
            continue  # not enough baseline data for this signal yet

        numeric_value = _signal_to_numeric(signal_name, signal_data)
        if numeric_value is None:
            continue

        bsl = baseline_signals[signal_name]
        mean = bsl.get("mean", numeric_value)
        std = bsl.get("std_dev", 0.0)
        z = _z_score(numeric_value, mean, std)

        evaluations.append(
            SignalEvaluation(
                signal=signal_name,
                current_value=numeric_value,
                baseline_mean=mean,
                baseline_std=std,
                z_score=round(z, 4),
                flagged=z >= _SIGNAL_Z_FLAG_THRESHOLD,
            )
        )

    flagged = [e for e in evaluations if e.flagged]
    signals_flagged_names = [e.signal for e in flagged]

    if not evaluations:
        return DriftEvaluation(
            drift_score=0.0,
            triggered=False,
            tier=None,
            tier_label=None,
            confidence_score=0.0,
            signals_flagged=[],
            message="No scoreable signals in this observation.",
        )

    # Composite drift score — weighted average of normalised z-scores
    total_weight = 0.0
    weighted_sum = 0.0
    for ev in flagged:
        w = _SIGNAL_WEIGHTS.get(ev.signal, 1.0)
        # Normalise z-score to 0–1 range (capped at z=5 = score 1.0)
        normalised = min(ev.z_score / 5.0, 1.0)
        weighted_sum += w * normalised
        total_weight += w

    raw_score = (weighted_sum / total_weight) if total_weight > 0 else 0.0

    # Risk profile sensitivity multiplier
    sensitivity = {"low": 0.85, "medium": 1.0, "high": 1.20}.get(risk_profile, 1.0)
    drift_score = round(min(raw_score * sensitivity, 1.0), 4)

    # Tier classification
    thresholds = settings.drift_thresholds
    tier, tier_label = _classify_tier(drift_score, thresholds)
    triggered = tier is not None

    # Confidence: based on number of scored signals vs total submitted
    confidence = round(len(evaluations) / max(len(signals), 1), 4)

    # Clinical pattern matching (UTI / infection pattern detection)
    clinical_pattern = None
    if triggered and signals_flagged_names:
        clinical_pattern = match_clinical_pattern(signals, signals_flagged_names)

    return DriftEvaluation(
        drift_score=drift_score,
        triggered=triggered,
        tier=tier,
        tier_label=tier_label,
        confidence_score=confidence,
        signals_flagged=signals_flagged_names,
        signal_details=evaluations,
        clinical_pattern=clinical_pattern,
    )


def _classify_tier(
    score: float, thresholds: dict[str, float]
) -> tuple[str | None, str | None]:
    """Map a drift score to a tier. Returns (None, None) if below T1 threshold."""
    tier_labels = {"T1": "Watch", "T2": "Concern", "T3": "Alert", "T4": "Critical"}
    # Check highest tier first
    for tier in ["T4", "T3", "T2", "T1"]:
        if score >= thresholds[tier]:
            return tier, tier_labels[tier]
    return None, None
