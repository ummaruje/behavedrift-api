import pytest
from httpx import AsyncClient

from app.models.tenant import Tenant

@pytest.mark.asyncio
async def test_get_correlations(client: AsyncClient, active_tenant_token: str):
    headers = {"Authorization": f"Bearer {active_tenant_token}"}
    response = await client.get("/v1/analytics/correlations?days=30", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "analysis_period_days" in data
    assert data["analysis_period_days"] == 30
    assert "strongest_correlations" in data
    assert isinstance(data["strongest_correlations"], list)
    assert len(data["strongest_correlations"]) > 0

@pytest.mark.asyncio
async def test_population_risk(client: AsyncClient, active_tenant_token: str):
    headers = {"Authorization": f"Bearer {active_tenant_token}"}
    response = await client.get("/v1/analytics/population?location=all", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "total_residents" in data
    assert "risk_distribution" in data
