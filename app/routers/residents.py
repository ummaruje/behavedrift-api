"""Router: /v1/residents — resident registration and baseline management."""

from __future__ import annotations


from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth.dependencies import get_current_tenant
from app.database import get_db
from app.exceptions import NotFoundError, ConflictError
from app.models.resident import Resident
from app.models.observation import Observation
from app.models.alert import Alert
from app.models.tenant import Tenant
from app.schemas.resident import (
    ResidentCreate,
    ResidentResponse,
    BaselineSummary,
    BaselineReset,
    ResidentList,
)
from datetime import datetime, timezone

router = APIRouter(prefix="/v1/residents", tags=["Residents"])


def _to_response(r: Resident) -> dict:
    from app.config import get_settings

    return {
        "resident_id": r.id,
        "internal_reference": r.internal_reference,
        "baseline_status": r.baseline_status,
        "baseline_window_days": r.baseline_window_days,
        "risk_profile": r.risk_profile,
        "diagnosis_codes": r.diagnosis_codes or [],
        "total_observations": r.total_observations,
        "min_observations_required": get_settings().baseline_min_observations,
        "created_at": r.created_at,
        "last_observation_at": r.last_observation_at,
    }


@router.post("", response_model=ResidentResponse, status_code=status.HTTP_201_CREATED)
async def create_resident(
    payload: ResidentCreate,
    tenant: Annotated[Tenant, Depends(get_current_tenant)],
    db: AsyncSession = Depends(get_db),
):
    """Register a new resident and initialise their baseline profile."""
    # Check uniqueness within tenant
    existing = await db.execute(
        select(Resident).where(
            Resident.tenant_id == tenant.id,
            Resident.internal_reference == payload.internal_reference,
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError(
            f"A resident with internal_reference '{payload.internal_reference}' already exists."
        )

    resident = Resident(
        tenant_id=tenant.id,
        internal_reference=payload.internal_reference,
        date_of_birth=payload.date_of_birth,
        diagnosis_codes=payload.diagnosis_codes or [],
        baseline_window_days=payload.baseline_window_days,
        risk_profile=payload.risk_profile,
        notes=payload.notes,
        baseline_status="initialising",
        total_observations=0,
    )
    db.add(resident)
    await db.flush()
    return _to_response(resident)


@router.get("", response_model=ResidentList)
async def list_residents(
    tenant: Annotated[Tenant, Depends(get_current_tenant)],
    db: AsyncSession = Depends(get_db),
    page: int = 1,
    page_size: int = 20,
    baseline_status: str | None = None,
    risk_profile: str | None = None,
):
    """List all residents for the authenticated tenant."""
    q = select(Resident).where(Resident.tenant_id == tenant.id)
    if baseline_status:
        q = q.where(Resident.baseline_status == baseline_status)
    if risk_profile:
        q = q.where(Resident.risk_profile == risk_profile)

    # Count total
    from sqlalchemy import func

    count_result = await db.execute(select(func.count()).select_from(q.subquery()))
    total = count_result.scalar_one()

    # Paginate
    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    residents = result.scalars().all()

    return {
        "residents": [_to_response(r) for r in residents],
        "meta": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_next": (page * page_size) < total,
        },
    }


@router.get("/{resident_id}", response_model=ResidentResponse)
async def get_resident(
    resident_id: str,
    tenant: Annotated[Tenant, Depends(get_current_tenant)],
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resident).where(
            Resident.id == resident_id, Resident.tenant_id == tenant.id
        )
    )
    resident = result.scalar_one_or_none()
    if not resident:
        raise NotFoundError(f"Resident '{resident_id}' not found.")
    return _to_response(resident)


@router.delete("/{resident_id}", status_code=status.HTTP_200_OK)
async def delete_resident(
    resident_id: str,
    tenant: Annotated[Tenant, Depends(get_current_tenant)],
    db: AsyncSession = Depends(get_db),
):
    """Permanently delete a resident and all their data (GDPR Article 17)."""
    result = await db.execute(
        select(Resident).where(
            Resident.id == resident_id, Resident.tenant_id == tenant.id
        )
    )
    resident = result.scalar_one_or_none()
    if not resident:
        raise NotFoundError(f"Resident '{resident_id}' not found.")

    # Count records before deletion
    obs_count = (
        (
            await db.execute(
                select(Observation).where(Observation.resident_id == resident_id)
            )
        )
        .scalars()
        .all()
    )
    alert_count = (
        (await db.execute(select(Alert).where(Alert.resident_id == resident_id)))
        .scalars()
        .all()
    )

    await db.delete(resident)
    await db.flush()

    import uuid

    return {
        "deleted_resident_id": resident_id,
        "certificate_id": f"del_{uuid.uuid4().hex[:12]}",
        "deleted_at": datetime.now(timezone.utc),
        "records_deleted": {
            "observations": len(obs_count),
            "alerts": len(alert_count),
            "baseline_snapshots": 1,
        },
    }


@router.get("/{resident_id}/baseline", response_model=BaselineSummary)
async def get_baseline(
    resident_id: str,
    tenant: Annotated[Tenant, Depends(get_current_tenant)],
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resident).where(
            Resident.id == resident_id, Resident.tenant_id == tenant.id
        )
    )
    resident = result.scalar_one_or_none()
    if not resident:
        raise NotFoundError(f"Resident '{resident_id}' not found.")

    baseline_data = resident.baseline_data or {}
    return {
        "resident_id": resident.id,
        "baseline_status": resident.baseline_status,
        "window_days": resident.baseline_window_days,
        "window_start": baseline_data.get("window_start"),
        "window_end": baseline_data.get("window_end"),
        "total_observations_in_window": baseline_data.get(
            "total_observations_in_window", 0
        ),
        "signals": baseline_data.get("signals", {}),
        "last_calculated_at": baseline_data.get("last_calculated_at"),
    }


@router.put("/{resident_id}/baseline/reset")
async def reset_baseline(
    resident_id: str,
    payload: BaselineReset,
    tenant: Annotated[Tenant, Depends(get_current_tenant)],
    db: AsyncSession = Depends(get_db),
):
    """Reset a resident's baseline (e.g. after hospitalisation)."""
    result = await db.execute(
        select(Resident).where(
            Resident.id == resident_id, Resident.tenant_id == tenant.id
        )
    )
    resident = result.scalar_one_or_none()
    if not resident:
        raise NotFoundError(f"Resident '{resident_id}' not found.")

    resident.baseline_data = None
    resident.baseline_status = "initialising"
    resident.baseline_last_calculated_at = None
    resident.baseline_reset_at = datetime.now(timezone.utc)
    resident.baseline_reset_reason = payload.reason
    await db.flush()

    from app.config import get_settings

    return {
        "resident_id": resident.id,
        "baseline_status": "initialising",
        "reset_at": resident.baseline_reset_at,
        "min_observations_required": get_settings().baseline_min_observations,
    }


# ---- GDPR Article 17 — Right to Erasure ----


@router.delete("/{resident_id}/gdpr/erase", status_code=status.HTTP_200_OK)
async def gdpr_erase_resident(
    resident_id: str,
    tenant: Annotated[Tenant, Depends(get_current_tenant)],
    db: AsyncSession = Depends(get_db),
):
    """
    Permanently erase all data for a resident under UK GDPR Article 17.

    This deletes the resident record and all associated observations, alerts,
    and baseline snapshots. A verifiable deletion certificate is returned.

    **This action is irreversible.**
    """
    result = await db.execute(
        select(Resident).where(
            Resident.id == resident_id, Resident.tenant_id == tenant.id
        )
    )
    resident = result.scalar_one_or_none()
    if not resident:
        raise NotFoundError(f"Resident '{resident_id}' not found.")

    # Count records before deletion for the certificate
    obs_result = await db.execute(
        select(Observation).where(Observation.resident_id == resident_id)
    )
    obs_count = len(obs_result.scalars().all())
    alert_result = await db.execute(
        select(Alert).where(Alert.resident_id == resident_id)
    )
    alert_count = len(alert_result.scalars().all())

    # Cascade delete
    await db.delete(resident)
    await db.flush()

    import uuid

    certificate_id = f"gdpr_del_{uuid.uuid4().hex[:12]}"

    return {
        "deleted_resident_id": resident_id,
        "certificate_id": certificate_id,
        "deleted_at": datetime.now(timezone.utc),
        "gdpr_article": "Article 17 — Right to Erasure",
        "records_deleted": {
            "observations": obs_count,
            "alerts": alert_count,
            "baseline_snapshots": 1,
        },
        "verification": (
            f"All personal data for resident '{resident_id}' has been permanently "
            f"erased. Certificate: {certificate_id}"
        ),
    }
