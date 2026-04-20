"""Router: /v1/observations — ingest observation data points."""

from __future__ import annotations


from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth.dependencies import get_current_tenant
from app.database import get_db
from app.exceptions import NotFoundError
from app.models.observation import Observation
from app.models.resident import Resident
from app.models.alert import Alert
from app.models.tenant import Tenant
from app.schemas.observation import (
    ObservationCreate,
    ObservationResponse,
    ObservationBatchRequest,
    ObservationBatchResponse,
)
from app.services.drift_engine import evaluate_drift
from app.services.baseline import should_recalculate, update_resident_baseline
from app.services.fhir_mapper import parse_fhir_observation

router = APIRouter(prefix="/v1/observations", tags=["Observations"])


# ---- Helper ----


async def _get_resident_or_404(
    resident_id: str, tenant: Tenant, db: AsyncSession
) -> Resident:
    result = await db.execute(
        select(Resident).where(
            Resident.id == resident_id,
            Resident.tenant_id == tenant.id,
        )
    )
    resident = result.scalar_one_or_none()
    if not resident:
        raise NotFoundError(f"Resident '{resident_id}' not found.")
    return resident


async def _process_single_observation(
    payload: ObservationCreate,
    tenant: Tenant,
    db: AsyncSession,
) -> dict:
    """Core logic for processing one observation. Returns a dict for the response."""
    resident = await _get_resident_or_404(payload.resident_id, tenant, db)

    # Recalculate baseline if stale
    if await should_recalculate(resident):
        resident = await update_resident_baseline(resident, db)

    # Run drift evaluation
    evaluation = evaluate_drift(
        signals=payload.signals.model_dump(exclude_none=True),
        baseline_data=resident.baseline_data or {},
        risk_profile=resident.risk_profile,
    )

    # Persist observation
    signals_dict = payload.signals.model_dump(exclude_none=True)
    obs = Observation(
        resident_id=resident.id,
        tenant_id=tenant.id,
        observed_at=payload.observed_at,
        observer_id=payload.observer_id,
        signals=signals_dict,
        context=(
            payload.context.model_dump(exclude_none=True) if payload.context else None
        ),
        drift_score=evaluation.drift_score,
        drift_triggered=evaluation.triggered,
        signals_flagged=evaluation.signals_flagged,
    )
    db.add(obs)

    # Update resident stats
    resident.total_observations = (resident.total_observations or 0) + 1
    resident.last_observation_at = payload.observed_at
    await db.flush()

    # Generate alert if drift triggered
    alert_summary = None
    if evaluation.triggered and evaluation.tier:
        explanation = {
            "summary": _build_explanation_summary(evaluation),
            "signals": [
                {
                    "signal": s.signal,
                    "current_value": s.current_value,
                    "baseline_mean": s.baseline_mean,
                    "baseline_std": s.baseline_std,
                    "z_score": s.z_score,
                }
                for s in evaluation.signal_details
            ],
            "clinical_correlation": evaluation.clinical_pattern,
        }
        alert = Alert(
            resident_id=resident.id,
            tenant_id=tenant.id,
            tier=evaluation.tier,
            tier_label=evaluation.tier_label,
            drift_score=evaluation.drift_score,
            confidence_score=evaluation.confidence_score,
            explanation=explanation,
        )
        db.add(alert)
        await db.flush()
        alert_summary = {
            "alert_id": alert.id,
            "tier": alert.tier,
            "tier_label": alert.tier_label,
        }

    return {
        "observation_id": obs.id,
        "resident_id": resident.id,
        "processed_at": datetime.now(timezone.utc),
        "drift_evaluation": {
            "triggered": evaluation.triggered,
            "drift_score": evaluation.drift_score,
            "baseline_status": resident.baseline_status,
            "signals_flagged": evaluation.signals_flagged,
            "alert_generated": alert_summary,
            "message": evaluation.message,
        },
        "status": "processed",
    }


def _build_explanation_summary(evaluation) -> str:
    n = len(evaluation.signals_flagged)
    if n == 0:
        return "No signals deviated significantly from baseline."
    signals_str = ", ".join(evaluation.signals_flagged)
    return (
        f"Resident is showing a sustained pattern change across {n} signal"
        f"{'s' if n > 1 else ''}: {signals_str}. "
        f"Drift score: {evaluation.drift_score:.2f} (Tier {evaluation.tier})."
    )


# ---- Routes ----


@router.post(
    "", response_model=ObservationResponse, status_code=status.HTTP_201_CREATED
)
async def create_observation(
    payload: ObservationCreate,
    tenant: Annotated[Tenant, Depends(get_current_tenant)],
    db: AsyncSession = Depends(get_db),
):
    """Submit a single behavioural observation for drift evaluation."""
    result = await _process_single_observation(payload, tenant, db)
    return result


@router.post(
    "/batch", response_model=ObservationBatchResponse, status_code=status.HTTP_200_OK
)
async def create_observation_batch(
    payload: ObservationBatchRequest,
    tenant: Annotated[Tenant, Depends(get_current_tenant)],
    db: AsyncSession = Depends(get_db),
):
    """Submit up to 100 observations in a single request."""
    results = []
    errors = []

    for idx, obs_payload in enumerate(payload.observations):
        try:
            result = await _process_single_observation(obs_payload, tenant, db)
            results.append(result)
        except Exception as e:
            errors.append(
                {
                    "index": idx,
                    "error": type(e).__name__,
                    "message": str(e),
                }
            )

    return {
        "submitted": len(payload.observations),
        "processed": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors,
    }


# ---- FHIR R4 Observation ingestion ----


@router.post("/fhir", status_code=status.HTTP_201_CREATED)
async def create_fhir_observation(
    fhir_resource: dict,
    tenant: Annotated[Tenant, Depends(get_current_tenant)],
    db: AsyncSession = Depends(get_db),
):
    """
    Accept a FHIR R4 Observation resource and map it to internal signals.
    Supported SNOMED codes are mapped to BehaveDrift signals automatically.
    """
    resident_id, observed_at, signals_dict = parse_fhir_observation(fhir_resource)

    # Process directly — we bypass Pydantic schema validation for signals since
    # FHIR values may not perfectly match the enumerated types
    resident = await _get_resident_or_404(resident_id, tenant, db)

    from app.services.baseline import should_recalculate, update_resident_baseline

    if await should_recalculate(resident):
        resident = await update_resident_baseline(resident, db)

    evaluation = evaluate_drift(
        signals=signals_dict,
        baseline_data=resident.baseline_data or {},
        risk_profile=resident.risk_profile,
    )

    obs = Observation(
        resident_id=resident.id,
        tenant_id=tenant.id,
        observed_at=observed_at,
        signals=signals_dict,
        drift_score=evaluation.drift_score,
        drift_triggered=evaluation.triggered,
        signals_flagged=evaluation.signals_flagged,
    )
    db.add(obs)
    resident.total_observations = (resident.total_observations or 0) + 1
    resident.last_observation_at = observed_at  # type: ignore[assignment]
    await db.flush()

    return {
        "observation_id": obs.id,
        "resident_id": resident.id,
        "processed_at": datetime.now(timezone.utc),
        "drift_evaluation": {
            "triggered": evaluation.triggered,
            "drift_score": evaluation.drift_score,
            "baseline_status": resident.baseline_status,
            "signals_flagged": evaluation.signals_flagged,
            "alert_generated": None,
            "message": evaluation.message,
        },
        "status": "processed",
    }


# ---- Observation history ----


@router.get("/{resident_id}")
async def get_observation_history(
    resident_id: str,
    tenant: Annotated[Tenant, Depends(get_current_tenant)],
    db: AsyncSession = Depends(get_db),
    start_date: str | None = None,
    end_date: str | None = None,
    signal: str | None = None,
    page: int = 1,
    page_size: int = 50,
):
    """Retrieve paginated observation history for a resident."""
    from sqlalchemy import func as sqla_func

    # Verify resident exists
    await _get_resident_or_404(resident_id, tenant, db)

    q = select(Observation).where(
        Observation.resident_id == resident_id,
        Observation.tenant_id == tenant.id,
    )

    if start_date:
        from dateutil.parser import isoparse  # type: ignore[import-untyped]

        q = q.where(Observation.observed_at >= isoparse(start_date))
    if end_date:
        from dateutil.parser import isoparse  # type: ignore[import-untyped]

        q = q.where(Observation.observed_at <= isoparse(end_date))

    # Count total
    count_result = await db.execute(select(sqla_func.count()).select_from(q.subquery()))
    total = count_result.scalar_one()

    # Paginate
    q = q.order_by(Observation.observed_at.desc())
    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    observations = result.scalars().all()

    obs_list = []
    for obs in observations:
        signals_data = obs.signals or {}
        # Apply signal filter if specified
        if signal and signal not in signals_data:
            continue
        obs_list.append(
            {
                "observation_id": obs.id,
                "resident_id": obs.resident_id,
                "observed_at": obs.observed_at,
                "observer_id": obs.observer_id,
                "signals": (
                    signals_data if not signal else {signal: signals_data.get(signal)}
                ),
                "context": obs.context,
                "drift_score": obs.drift_score,
                "drift_triggered": obs.drift_triggered,
                "processed_at": obs.processed_at,
            }
        )

    return {
        "resident_id": resident_id,
        "observations": obs_list,
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_next": (page * page_size) < total,
        },
    }
