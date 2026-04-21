# Integration Guide

BehaveDrift API is an event-driven engine intended to securely consume unstructured behavioural data and push out actionable drift alerts. We offer a series of integration patterns ranging from straightforward API consumption to enterprise-grade EHR connectors.

This guide details the integration mechanisms requested in our documentation standard.

---

<br>

<a id="nourish"></a>
## Integrate with Nourish Care

Nourish Care is a widely deployed digital social care records platform. 

### Mechanism: Daily Sync / Realtime Pushing
Nourish interactions can be exported and transformed into BehaveDrift observations.

1. **Extraction**: Subscribe to the Nourish export stream or utilize their outbound Webhooks for significant interaction categories (e.g., `Sleep Chart`, `Fluid Intake`, `Mood Review`).
2. **Translation**: Map Nourish categories directly into BehaveDrift's taxonomy. 
   - Nourish 'Sleep Chart' `awake` maps to BehaveDrift's `sleep_quality.night_wakings`.
   - Nourish 'Pain assessment' maps to BehaveDrift's `pain_indicators.painad_score`.
3. **Transmission**: Send the payload securely to `POST /v1/observations/`.

> [!TIP]
> **Data Normalisation**
> You don't need to align times exactly. Submit the observations as they occurred (`observed_at`). BehaveDrift aggregates and groups the signals natively within its predefined `window_start` cycles.

---

<a id="radar-healthcare"></a>
## Integrate with Radar Healthcare

Radar Healthcare is uniquely suited to consume output *Generated Alerts* from our system to escalate risks directly to your quality and compliance teams.

### Mechanism: Webhook Consumption
Radar incident systems map effectively onto BehaveDrift Webhook schemas.

1. **Create Target Node**: Within Radar Healthcare, configure an inbound listener or external service gateway endpoint for *Behavioral Incident Alerts*.
2. **Subscribe**: Within your BehaveDrift Tenant CLI, configure a webhook targeting the new endpoint. You can restrict the events to `alert.triggered`.
3. **Thresholding**: We strongly recommend only forwarding `T3` (Warning) and `T4` (Critical) tiers to Radar Healthcare, as `T1`/`T2` represent early warnings that might pollute typical incident management boards.

---

<a id="webhooks"></a>
## Set up webhooks

You should proactively receive alerts rather than polling the `GET /v1/alerts/` endpoints. 

### Webhook Configuration
BehaveDrift webhooks dispatch signed JSON payloads to any HTTP target endpoint.

1. Register a webhook via `POST /v1/webhooks`. Provide your endpoint `url` and the list of `events` you wish to subscribe to.
2. The registration payload response will return a unique `signing_secret`.

### Validating Payloads
Every emitted webhook contains a distinct cryptography signature header: `X-BehaveDrift-Signature`. 

> [!IMPORTANT]
> **Security Requirement** 
> To prevent spoofing, always compute the `HMAC SHA-256` signature of the raw request body using your provisioned `signing_secret` and assert equality against the received header.

```python
import hmac
import hashlib

def verify_signature(payload: bytes, secret: str, signature: str) -> bool:
    expected = hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

---

<a id="fhir-r4"></a>
## FHIR R4 Integration

For enterprise environments with legacy integration engines or those strictly following standard interoperability guidelines, BehaveDrift offers limited mapping out to FHIR R4 standard.

### Concept Models
* **Residents** map to `Patient`.
* **Observations** map to `Observation` (specifically mental-health and vital groupings).
* **Alerts** map to `RiskAssessment` and `ClinicalImpression`.

### Exports
Instead of fetching disparate endpoints, you can trigger a bulk FHIR extraction using the analytics services: `GET /v1/analytics/export?format=fhir_bundle`. 

> [!WARNING]
> Ensure your consuming client contains permissions required to securely resolve the full FHIR Bundle mapping logic. Not all standard internal drift scores neatly resolve to canonical FHIR nomenclatures; extension blocks are frequently used.
