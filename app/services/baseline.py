"""
Baseline profiling service.

Computes per-signal statistics (mean, std_dev, most_common) from a
resident's historical observations within their configured window.

The baseline is recalculated periodically (controlled by
baseline_recalculation_interval_hours) and stored as JSON on the
Resident row — avoiding expensive real-time calculation on every observation.
"""

from __future__ import annotations

import math
import statistics
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.observation import Observation
from app.models.resident import Resident
from app.services.drift_engine import _signal_to_numeric

settings = get_settings()


async def build_baseline(
    resident: Resident,
    db: AsyncSession,
) -> dict[str, Any] | None:
    """
    Recalculate and return the baseline statistics for a resident.

    Args:
        resident: The Resident ORM object.
        db: Active async DB session.

    Returns:
        Baseline dict (to be stored in resident.baseline_data), or None
        if there are insufficient observations.
    """
    window_start = datetime.now(timezone.utc) - timedelta(
        days=resident.baseline_window_days
    )

    result = await db.execute(
        select(Observation)
        .where(
            and_(
                Observation.resident_id == resident.id,
                Observation.observed_at >= window_start,
            )
        )
        .order_by(Observation.observed_at.asc())
    )
    observations = result.scalars().all()

    if len(observations) < settings.baseline_min_observations:
        return None

    # Per-signal value lists
    signal_values: dict[str, list[float]] = {}
    signal_categorical: dict[str, list[str]] = {}

    for obs in observations:
        for signal_name, signal_data in obs.signals.items():
            numeric = _signal_to_numeric(signal_name, signal_data)
            if numeric is not None:
                signal_values.setdefault(signal_name, []).append(numeric)
            # Also track raw categorical values
            raw_val = signal_data.get("value")
            if isinstance(raw_val, str):
                signal_categorical.setdefault(signal_name, []).append(raw_val)

    processed_signals: dict[str, dict] = {}
    total_obs = len(observations)

    for signal_name, values in signal_values.items():
        mean = statistics.mean(values)
        # Apply recency weighting — recent observations count more
        std = _weighted_std(values, weight_factor=settings.baseline_recency_weight)
        cats = signal_categorical.get(signal_name, [])
        most_common = Counter(cats).most_common(1)[0][0] if cats else None

        processed_signals[signal_name] = {
            "mean": round(mean, 6),
            "std_dev": round(std, 6),
            "most_common": most_common,
            "sample_count": len(values),
        }

    return {
        "window_days": resident.baseline_window_days,
        "window_start": window_start.isoformat(),
        "window_end": datetime.now(timezone.utc).isoformat(),
        "total_observations_in_window": total_obs,
        "signals": processed_signals,
        "last_calculated_at": datetime.now(timezone.utc).isoformat(),
    }


def _weighted_std(values: list[float], weight_factor: float = 1.5) -> float:
    """
    Compute a recency-weighted standard deviation.

    More recent observations (later in the list) are assigned higher weights.
    weight_factor > 1.0 amplifies recency bias.
    """
    n = len(values)
    if n < 2:
        return 0.0

    # Linear weights: oldest = 1.0, newest = weight_factor
    weights = [1.0 + (weight_factor - 1.0) * (i / (n - 1)) for i in range(n)]
    total_weight = sum(weights)

    weighted_mean = sum(w * v for w, v in zip(weights, values)) / total_weight
    variance = (
        sum(w * (v - weighted_mean) ** 2 for w, v in zip(weights, values))
        / total_weight
    )

    return math.sqrt(variance)


async def should_recalculate(resident: Resident) -> bool:
    """
    Returns True if the baseline should be recalculated.
    Avoids recalculating on every observation submission.
    """
    if not resident.baseline_last_calculated_at:
        return True

    cutoff = datetime.now(timezone.utc) - timedelta(
        hours=settings.baseline_recalculation_interval_hours
    )
    return resident.baseline_last_calculated_at < cutoff


async def update_resident_baseline(resident: Resident, db: AsyncSession) -> Resident:
    """
    Recalculate and persist the baseline for a resident.
    Updates the resident row in-place.
    """
    baseline = await build_baseline(resident, db)

    if baseline is None:
        resident.baseline_status = "initialising"
    else:
        resident.baseline_data = baseline
        resident.baseline_status = "active"
        resident.baseline_last_calculated_at = datetime.now(timezone.utc)

    await db.flush()
    return resident
