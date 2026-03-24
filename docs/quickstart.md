# Quickstart Guide

**Get your first drift alert in under 5 minutes.**

---

## Prerequisites

- Docker and Docker Compose installed
- `curl` or any HTTP client

---

## Step 1 — Clone and Start

```bash
git clone https://github.com/umarisa/behavedrift-api.git
cd behavedrift-api

cp .env.example .env

docker-compose up -d

# Wait ~10 seconds for the database to initialise, then verify:
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected"
}
```

---

## Step 2 — Get an API Key

```bash
curl -X POST http://localhost:8000/v1/auth/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "organisation_name": "My Care Home",
    "contact_email": "admin@mycarehome.co.uk"
  }'
```

**Response:**
```json
{
  "tenant_id": "ten_abc123",
  "api_key": "bda_sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "message": "Store this API key securely — it will not be shown again."
}
```

> ⚠️ **Save the `api_key`** — it is shown only once.

Set it as a shell variable for the rest of this guide:
```bash
export API_KEY="bda_sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

---

## Step 3 — Register a Resident

```bash
curl -X POST http://localhost:8000/v1/residents \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "internal_reference": "RES-001",
    "date_of_birth": "1938-04-15",
    "diagnosis_codes": ["F00.1"],
    "baseline_window_days": 28,
    "risk_profile": "high"
  }'
```

**Response:**
```json
{
  "resident_id": "res_7f3a9c21",
  "internal_reference": "RES-001",
  "baseline_status": "initialising",
  "min_observations_required": 14,
  "created_at": "2026-03-14T12:00:00Z"
}
```

Store the `resident_id`:
```bash
export RESIDENT_ID="res_7f3a9c21"
```

---

## Step 4 — Submit Your First Observation

```bash
curl -X POST http://localhost:8000/v1/observations \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"resident_id\": \"$RESIDENT_ID\",
    \"observed_at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
    \"signals\": {
      \"mood\": { \"value\": 2, \"scale\": \"1-5\" },
      \"appetite\": { \"value\": \"poor\" },
      \"sleep_quality\": { \"value\": \"disturbed\", \"night_wakings\": 4 },
      \"social_engagement\": { \"value\": \"withdrawn\" }
    }
  }"
```

**Response:**
```json
{
  "observation_id": "obs_a9d2f1c3",
  "processed_at": "2026-03-14T12:00:05Z",
  "drift_evaluation": {
    "triggered": false,
    "drift_score": 0.0,
    "baseline_status": "initialising",
    "message": "Baseline is still being established. Submit at least 14 observations to enable drift detection."
  },
  "status": "processed"
}
```

> **Note:** Drift detection activates after 14 observations. Submit observations over multiple simulated days, or use the seed script to fast-track: `make seed-demo-data RESIDENT_ID=$RESIDENT_ID`

---

## Step 5 — Check for Alerts

Once baseline is established, check for active alerts:

```bash
curl http://localhost:8000/v1/alerts/$RESIDENT_ID \
  -H "X-API-Key: $API_KEY"
```

**Example alert response:**
```json
{
  "alerts": [
    {
      "alert_id": "alr_3c8e1b90",
      "tier": "T2",
      "tier_label": "Concern",
      "confidence_score": 0.74,
      "explanation": {
        "summary": "Resident is showing a sustained pattern change across 3 signals over the past 72 hours. Mood is 1.8 standard deviations below 28-day baseline. Combined with reduced appetite and social withdrawal, this pattern is consistent with early-stage infection indicators.",
        "suggested_actions": [
          "Check fluid intake over past 48 hours",
          "Observe for UTI indicators",
          "Consider requesting urine dipstick test",
          "Notify responsible clinical lead"
        ]
      }
    }
  ]
}
```

---

## Next Steps

| Goal | Where to go |
|------|------------|
| Integrate with Nourish | [docs/integration-guide.md](integration-guide.md#nourish) |
| Integrate with Radar Healthcare | [docs/integration-guide.md](integration-guide.md#radar-healthcare) |
| Set up webhooks | [docs/integration-guide.md](integration-guide.md#webhooks) |
| FHIR R4 integration | [docs/integration-guide.md](integration-guide.md#fhir-r4) |
| Full API reference | [http://localhost:8000/docs](http://localhost:8000/docs) |
| Run in production | [docs/deployment.md](deployment.md) |
| Auth with OAuth2 | [docs/adr/ADR-003-auth-model.md](adr/ADR-003-auth-model.md) |

---

## Common Issues

**Container won't start:**
```bash
docker-compose logs api
# Check database connection in .env
```

**401 Unauthorized:**
```bash
# Check your API key is correct and passed in X-API-Key header
curl http://localhost:8000/v1/residents \
  -H "X-API-Key: bda_sk_your_key_here"
```

**Drift not triggering:**  
The resident needs at least 14 observations before the baseline is valid. Use `make seed-demo-data` to generate test data quickly.

**Need help?** → [Open a question on GitHub](https://github.com/umarisa/behavedrift-api/issues/new?template=question.md)
