import pytest
import pytest_asyncio
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from app.models.tenant import Tenant
from app.models.resident import Resident
from app.models.alert import Alert


@pytest_asyncio.fixture
async def setup_resident(db_session: AsyncSession, active_tenant: Tenant) -> Resident:
    resident = Resident(
        tenant_id=active_tenant.id,
        internal_reference="TEST-RES",
        date_of_birth=datetime.datetime(1940, 1, 1, tzinfo=datetime.timezone.utc),
        risk_profile="high",
    )
    db_session.add(resident)
    await db_session.commit()
    await db_session.refresh(resident)
    return resident


@pytest_asyncio.fixture
async def setup_alert(
    db_session: AsyncSession, active_tenant: Tenant, setup_resident: Resident
) -> Alert:
    alert = Alert(
        resident_id=setup_resident.id,
        tenant_id=active_tenant.id,
        tier="T3",
        tier_label="Alert",
        drift_score=0.8,
        confidence_score=0.9,
        explanation={"signals": [{"signal": "poor_sleep"}]},
    )
    db_session.add(alert)
    await db_session.commit()
    await db_session.refresh(alert)
    return alert


@pytest.mark.asyncio
async def test_get_resident_alerts(
    client: AsyncClient,
    active_tenant_token: str,
    setup_resident: Resident,
    setup_alert: Alert,
):
    headers = {"Authorization": f"Bearer {active_tenant_token}"}
    response = await client.get(f"/v1/alerts/{setup_resident.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["resident_id"] == setup_resident.id
    assert len(data["alerts"]) == 1
    assert data["alerts"][0]["tier"] == "T3"


@pytest.mark.asyncio
async def test_get_alert_detail(
    client: AsyncClient,
    active_tenant_token: str,
    setup_resident: Resident,
    setup_alert: Alert,
):
    headers = {"Authorization": f"Bearer {active_tenant_token}"}
    response = await client.get(f"/v1/alerts/{setup_alert.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["alert_id"] == setup_alert.id
    assert data["resident_id"] == setup_resident.id
    assert data["explanation"] is not None


@pytest.mark.asyncio
async def test_acknowledge_alert(
    client: AsyncClient,
    active_tenant_token: str,
    setup_resident: Resident,
    setup_alert: Alert,
):
    headers = {"Authorization": f"Bearer {active_tenant_token}"}
    payload = {
        "action_taken": "Treated patient with analgesics",
        "actioned_by": "Dr. Smith",
    }
    response = await client.post(
        f"/v1/alerts/{setup_alert.id}/acknowledge", headers=headers, json=payload
    )
    assert response.status_code == 200
    assert response.status_code == 200
    # Verify state via detail endpoint
    response2 = await client.get(f"/v1/alerts/{setup_alert.id}", headers=headers)
    data2 = response2.json()
    assert data2["metadata"]["action_taken"] == "Treated patient with analgesics"
    assert data2["metadata"]["acknowledged_by"] == "Dr. Smith"
    assert data2["metadata"]["acknowledged"] is True
