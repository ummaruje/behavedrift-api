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


@pytest.mark.asyncio
async def test_fhir_ingestion_generates_alert(
    client: AsyncClient,
    active_tenant_token: str,
    setup_resident: Resident,
    db_session: AsyncSession,
):
    headers = {"Authorization": f"Bearer {active_tenant_token}"}

    # 1. Establish a baseline for this resident.
    # Set the resident's baseline_data manually to simulate an active baseline.
    setup_resident.baseline_status = "active"
    setup_resident.baseline_data = {
        "signals": {"mood": {"mean": 4.5, "std_dev": 0.2, "sample_count": 20}}
    }
    db_session.add(setup_resident)
    await db_session.commit()

    # 2. Post a FHIR observation that causes a significant deterioration (mood=1).
    fhir_obs = {
        "resourceType": "Observation",
        "status": "final",
        "code": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "285854004",  # Emotion -> mood
                    "display": "Emotion",
                }
            ]
        },
        "subject": {"reference": f"Patient/{setup_resident.id}"},
        "effectiveDateTime": "2026-03-14T15:00:00Z",
        "valueInteger": 1,  # mood value of 1 against mean of 4.5 std 0.2 -> z=17.5!
    }

    response = await client.post(
        "/v1/observations/fhir", headers=headers, json=fhir_obs
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "processed"
    assert data["drift_evaluation"]["triggered"] is True
    assert data["drift_evaluation"]["alert_generated"] is not None
    alert_id = data["drift_evaluation"]["alert_generated"]["alert_id"]
    assert alert_id.startswith("alr_")

    # 3. Retrieve the generated alert to confirm it was stored in the database.
    response2 = await client.get(f"/v1/alerts/{alert_id}", headers=headers)
    assert response2.status_code == 200
    alert_data = response2.json()
    assert alert_data["alert_id"] == alert_id
    assert alert_data["resident_id"] == setup_resident.id
    assert alert_data["drift_score"] > 0.0
