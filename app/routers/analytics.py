"""Router: /v1/analytics — population-level analytics, trends, and export."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_tenant
from app.database import get_db
from app.models.tenant import Tenant
from app.schemas.analytics import PopulationRiskResponse, ResidentTrendResponse
from app.services.analytics import (
    calculate_population_risk,
    calculate_resident_trend,
    generate_export_csv,
)

router = APIRouter(prefix="/v1/analytics", tags=["Analytics"])


# ---- Population-level risk distribution ----


@router.get("/population", response_model=PopulationRiskResponse)
async def get_population_risk(
    tenant: Annotated[Tenant, Depends(get_current_tenant)],
    db: AsyncSession = Depends(get_db),
    location: str | None = None,
    date_param: date | None = Query(default=None, alias="date"),
):
    """
    Returns risk distribution and active alerts across all residents for the tenant.
    """
    return await calculate_population_risk(tenant.id, db, location)


# ---- Longitudinal drift trend for a resident ----


@router.get("/trends/{resident_id}", response_model=ResidentTrendResponse)
async def get_resident_trend(
    resident_id: str,
    tenant: Annotated[Tenant, Depends(get_current_tenant)],
    db: AsyncSession = Depends(get_db),
    days: int = Query(default=30, ge=7, le=365),
):
    """
    Returns time-series drift scores for a resident over the specified period.
    """
    return await calculate_resident_trend(resident_id, tenant.id, db, days)


# ---- Export ----


@router.get("/export")
async def export_report(
    tenant: Annotated[Tenant, Depends(get_current_tenant)],
    db: AsyncSession = Depends(get_db),
    format: str = Query(..., pattern="^(csv|pdf|fhir_bundle)$", alias="format"),
    resident_id: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    include_alerts: bool = True,
    include_observations: bool = False,
):
    """
    Export observation and/or alert data as CSV.
    PDF and FHIR Bundle formats are planned for a future release.
    """
    output = await generate_export_csv(
        tenant_id=tenant.id,
        db=db,
        format_type=format,
        resident_id=resident_id,
        start_date=start_date,
        end_date=end_date,
        include_alerts=include_alerts,
        include_observations=include_observations,
    )
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=behavedrift_export.csv"},
    )
