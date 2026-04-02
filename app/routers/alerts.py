"""Router: /v1/alerts — alert listing, acknowledgement, and dismissal."""

from typing import Annotated
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth.dependencies import get_current_tenant
from app.database import get_db
from app.exceptions import NotFoundError, ConflictError
from app.models.alert import Alert
from app.models.tenant import Tenant
from app.schemas.alert import AlertAcknowledge, AlertDismiss

router = APIRouter(prefix="/v1/alerts", tags=["Alerts"])


def _alert_to_response(a: Alert) -> dict:
    return {
        "alert_id": a.id,
        "resident_id": a.resident_id,
        "generated_at": a.generated_at,
        "tier": a.tier,
        "tier_label": a.tier_label,
        "confidence_score": a.confidence_score,
        "drift_score": a.drift_score,
        "explanation": a.explanation,
        "historical_context": a.historical_context,
        "metadata": a.metadata_dict,
    }


async def _get_alert_or_404(alert_id: str, tenant: Tenant, db: AsyncSession) -> Alert:
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id, Alert.tenant_id == tenant.id)
    )
    alert = result.scalar_one_or_none()
    if not alert:
        raise NotFoundError(f"Alert '{alert_id}' not found.")
    return alert


@router.get("")
async def list_alerts(
    tenant: Annotated[Tenant, Depends(get_current_tenant)],
    db: AsyncSession = Depends(get_db),
    tier: str | None = None,
    acknowledged: bool | None = None,
    page: int = 1,
    page_size: int = 20,
):
    """List all active (non-dismissed) drift alerts for the tenant."""
    q = select(Alert).where(
        Alert.tenant_id == tenant.id,
        Alert.dismissed == False,  # noqa: E712
    )
    if tier:
        q = q.where(Alert.tier == tier)
    if acknowledged is not None:
        q = q.where(Alert.acknowledged == acknowledged)

    from sqlalchemy import func
    count_result = await db.execute(select(func.count()).select_from(q.subquery()))
    total = count_result.scalar_one()

    q = q.order_by(Alert.generated_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    alerts = result.scalars().all()

    return {
        "alerts": [_alert_to_response(a) for a in alerts],
        "meta": {"total": total, "page": page, "page_size": page_size, "has_next": (page * page_size) < total},
    }


@router.get("/{resident_id}")
async def get_resident_alerts(
    resident_id: str,
    tenant: Annotated[Tenant, Depends(get_current_tenant)],
    db: AsyncSession = Depends(get_db),
    include_dismissed: bool = False,
):
    """Get all alerts for a specific resident."""
    q = select(Alert).where(
        Alert.resident_id == resident_id,
        Alert.tenant_id == tenant.id,
    )
    if not include_dismissed:
        q = q.where(Alert.dismissed == False)  # noqa: E712

    result = await db.execute(q.order_by(Alert.generated_at.desc()))
    alerts = result.scalars().all()
    return {"resident_id": resident_id, "alerts": [_alert_to_response(a) for a in alerts]}


@router.get("/detail/{alert_id}")
async def get_alert(
    alert_id: str,
    tenant: Annotated[Tenant, Depends(get_current_tenant)],
    db: AsyncSession = Depends(get_db),
):
    """Get full detail of a specific alert."""
    alert = await _get_alert_or_404(alert_id, tenant, db)
    return _alert_to_response(alert)


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    payload: AlertAcknowledge,
    tenant: Annotated[Tenant, Depends(get_current_tenant)],
    db: AsyncSession = Depends(get_db),
):
    """Acknowledge an alert and record the action taken."""
    alert = await _get_alert_or_404(alert_id, tenant, db)
    if alert.acknowledged:
        raise ConflictError(f"Alert '{alert_id}' has already been acknowledged.")

    alert.acknowledged = True
    alert.acknowledged_at = datetime.now(timezone.utc)
    alert.acknowledged_by = payload.actioned_by
    alert.action_taken = payload.action_taken
    await db.flush()
    return _alert_to_response(alert)


@router.delete("/{alert_id}")
async def dismiss_alert(
    alert_id: str,
    payload: AlertDismiss,
    tenant: Annotated[Tenant, Depends(get_current_tenant)],
    db: AsyncSession = Depends(get_db),
):
    """Dismiss an alert with a documented reason (retained in audit log)."""
    alert = await _get_alert_or_404(alert_id, tenant, db)
    alert.dismissed = True
    alert.dismissed_at = datetime.now(timezone.utc)
    alert.dismissed_by = payload.dismissed_by
    alert.dismiss_reason = payload.reason
    await db.flush()
    return {
        "alert_id": alert.id,
        "dismissed": True,
        "dismissed_at": alert.dismissed_at,
    }
