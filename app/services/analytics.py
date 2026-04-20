"""
Analytics Service
Extracts complex query logic for population risk, resident trends, and data export.
"""
from __future__ import annotations


import csv
import io
from datetime import datetime, date, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.exceptions import NotFoundError, ValidationError
from app.models.resident import Resident
from app.models.observation import Observation
from app.models.alert import Alert


async def calculate_population_risk(
    tenant_id: str, db: AsyncSession, location: str | None = None
) -> dict:
    """Calculates risk distribution and active alerts across all residents for the tenant."""
    # Count residents
    residents_q = select(Resident).where(Resident.tenant_id == tenant_id)
    result = await db.execute(residents_q)
    residents = result.scalars().all()
    total_residents = len(residents)

    # Fetch active alerts (non-dismissed)
    alerts_q = select(Alert).where(
        Alert.tenant_id == tenant_id,
        Alert.dismissed.is_(False),
    )
    alert_result = await db.execute(alerts_q)
    active_alerts = alert_result.scalars().all()

    tier_order = {"T4": 4, "T3": 3, "T2": 2, "T1": 1}
    resident_max_tier: dict[str, str] = {}
    for alert in active_alerts:
        current = resident_max_tier.get(alert.resident_id)
        if not current or tier_order.get(alert.tier, 0) > tier_order.get(current, 0):
            resident_max_tier[alert.resident_id] = alert.tier

    risk_dist = {
        "stable": 0,
        "watch_t1": 0,
        "concern_t2": 0,
        "alert_t3": 0,
        "critical_t4": 0,
    }
    for r in residents:
        tier = resident_max_tier.get(r.id)
        if not tier:
            risk_dist["stable"] += 1
        elif tier == "T1":
            risk_dist["watch_t1"] += 1
        elif tier == "T2":
            risk_dist["concern_t2"] += 1
        elif tier == "T3":
            risk_dist["alert_t3"] += 1
        elif tier == "T4":
            risk_dist["critical_t4"] += 1

    signal_counts: dict[str, int] = {}
    for alert in active_alerts:
        explanation = alert.explanation or {}
        signals = explanation.get("signals", [])
        for s in signals:
            name = s.get("signal", "")
            if name:
                signal_counts[name] = signal_counts.get(name, 0) + 1
    trending_signals = sorted(signal_counts, key=signal_counts.get, reverse=True)[:5]  # type: ignore[arg-type]

    alert_summaries = []
    for alert in active_alerts:
        explanation = alert.explanation or {}
        primary = [
            s.get("signal", "")
            for s in explanation.get("signals", [])
            if s.get("signal")
        ]
        alert_summaries.append(
            {
                "resident_id": alert.resident_id,
                "tier": alert.tier,
                "primary_signals": primary[:3],
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc),
        "location": location,
        "total_residents": total_residents,
        "risk_distribution": risk_dist,
        "trending_signals": trending_signals,
        "active_alerts": alert_summaries,
    }


async def calculate_resident_trend(
    resident_id: str, tenant_id: str, db: AsyncSession, days: int
) -> dict:
    """Returns time-series drift scores for a resident over the specified period."""
    result = await db.execute(
        select(Resident).where(
            Resident.id == resident_id,
            Resident.tenant_id == tenant_id,
        )
    )
    resident = result.scalar_one_or_none()
    if not resident:
        raise NotFoundError(f"Resident '{resident_id}' not found.")

    now = datetime.now(timezone.utc)
    period_start = now - timedelta(days=days)

    obs_result = await db.execute(
        select(Observation)
        .where(
            Observation.resident_id == resident_id,
            Observation.tenant_id == tenant_id,
            Observation.observed_at >= period_start,
        )
        .order_by(Observation.observed_at.asc())
    )
    observations = obs_result.scalars().all()

    alert_result = await db.execute(
        select(Alert).where(
            Alert.resident_id == resident_id,
            Alert.tenant_id == tenant_id,
            Alert.generated_at >= period_start,
        )
    )
    alerts = alert_result.scalars().all()
    alert_by_date: dict[date, str] = {}
    for alert in alerts:
        d = alert.generated_at.date()
        current = alert_by_date.get(d)
        tier_order = {"T4": 4, "T3": 3, "T2": 2, "T1": 1}
        if not current or tier_order.get(alert.tier, 0) > tier_order.get(current, 0):
            alert_by_date[d] = alert.tier

    daily_data: dict[date, list] = {}
    for obs in observations:
        d = obs.observed_at.date()
        daily_data.setdefault(d, []).append(obs)

    data_points = []
    for d in sorted(daily_data.keys()):
        obs_list = daily_data[d]
        scores = [o.drift_score for o in obs_list if o.drift_score is not None]
        avg_drift = sum(scores) / len(scores) if scores else None

        signal_summary: dict[str, list] = {}
        for obs in obs_list:
            if obs.signals:
                for sig_name, sig_data in obs.signals.items():
                    if isinstance(sig_data, dict) and "value" in sig_data:
                        val = sig_data["value"]
                        if isinstance(val, (int, float)):
                            signal_summary.setdefault(sig_name, []).append(val)

        averaged_signals = {}
        for k, v in signal_summary.items():
            if v:
                averaged_signals[k] = round(sum(v) / len(v), 2)

        data_points.append(
            {
                "date": d,
                "drift_score": round(avg_drift, 4) if avg_drift is not None else None,
                "signals": averaged_signals,
                "alert_tier": alert_by_date.get(d),
            }
        )

    return {
        "resident_id": resident_id,
        "period_start": period_start,
        "period_end": now,
        "data_points": data_points,
    }


async def generate_export_csv(
    tenant_id: str,
    db: AsyncSession,
    format_type: str,
    resident_id: str | None,
    start_date: date | None,
    end_date: date | None,
    include_alerts: bool,
    include_observations: bool,
) -> io.StringIO:
    """Generates a CSV export spanning observations and alerts."""
    if format_type in ("pdf", "fhir_bundle"):
        raise ValidationError(
            f"Export format '{format_type}' is not yet implemented. Use 'csv' for now."
        )

    output = io.StringIO()
    writer = csv.writer(output)

    if include_observations:
        writer.writerow(
            [
                "observation_id",
                "resident_id",
                "observed_at",
                "drift_score",
                "drift_triggered",
                "signals_flagged",
            ]
        )

        q = select(Observation).where(Observation.tenant_id == tenant_id)
        if resident_id:
            q = q.where(Observation.resident_id == resident_id)
        if start_date:
            q = q.where(
                Observation.observed_at
                >= datetime.combine(start_date, datetime.min.time()).replace(
                    tzinfo=timezone.utc
                )
            )
        if end_date:
            q = q.where(
                Observation.observed_at
                <= datetime.combine(end_date, datetime.max.time()).replace(
                    tzinfo=timezone.utc
                )
            )
        q = q.order_by(Observation.observed_at.desc()).limit(10000)

        result = await db.execute(q)
        for obs in result.scalars().all():
            writer.writerow(
                [
                    obs.id,
                    obs.resident_id,
                    obs.observed_at.isoformat(),
                    obs.drift_score,
                    obs.drift_triggered,
                    "; ".join(obs.signals_flagged or []),
                ]
            )

    if include_alerts:
        if include_observations:
            writer.writerow([])
        writer.writerow(
            [
                "alert_id",
                "resident_id",
                "generated_at",
                "tier",
                "tier_label",
                "drift_score",
                "confidence_score",
                "acknowledged",
                "dismissed",
            ]
        )

        q = select(Alert).where(Alert.tenant_id == tenant_id)  # type: ignore[assignment]
        if resident_id:
            q = q.where(Alert.resident_id == resident_id)
        if start_date:
            q = q.where(
                Alert.generated_at
                >= datetime.combine(start_date, datetime.min.time()).replace(
                    tzinfo=timezone.utc
                )
            )
        if end_date:
            q = q.where(
                Alert.generated_at
                <= datetime.combine(end_date, datetime.max.time()).replace(
                    tzinfo=timezone.utc
                )
            )
        q = q.order_by(Alert.generated_at.desc()).limit(10000)

        result = await db.execute(q)
        for alert in result.scalars().all():
            writer.writerow(
                [
                    alert.id,
                    alert.resident_id,
                    alert.generated_at.isoformat(),  # type: ignore[attr-defined]
                    alert.tier,  # type: ignore[attr-defined]
                    alert.tier_label,  # type: ignore[attr-defined]
                    alert.drift_score,
                    alert.confidence_score,  # type: ignore[attr-defined]
                    alert.acknowledged,  # type: ignore[attr-defined]
                    alert.dismissed,  # type: ignore[attr-defined]
                ]
            )

    output.seek(0)
    return output


async def calculate_correlations(tenant_id: str, db: AsyncSession, days: int) -> dict:
    """Basic mock implementation of correlation analysis."""
    # In a full implementation, this would join observations and alerts 
    # to find statistical correlations between time, staff, and behavior.
    return {
        "analysis_period_days": days,
        "strongest_correlations": [
            {
                "factor": "continuity_of_carer", 
                "correlation_coefficient": 0.72,
                "finding": "Higher staff continuity correlates with more stable drift scores."
            },
            {
                "factor": "time_of_day",
                "correlation_coefficient": 0.65,
                "finding": "Alert generation peaks between 16:00 and 18:00 (sundowning pattern)."
            }
        ]
    }
