# 🧠 BehaveDrift API
### Behavioural Pattern Drift Detection for Dementia & Cognitive Decline Care

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![API Version](https://img.shields.io/badge/API-v1.0.0-blue.svg)](https://github.com/umarisa/behavedrift-api)
[![OpenAPI 3.1](https://img.shields.io/badge/OpenAPI-3.1-orange.svg)](docs/openapi.yaml)
[![FHIR R4 Mapped](https://img.shields.io/badge/FHIR-R4%20Mapped-yellow.svg)](https://hl7.org/fhir/)
[![GDPR Article 25](https://img.shields.io/badge/GDPR-Article%2025%20Privacy%20by%20Design-blue.svg)](#security--compliance)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Swagger%20UI-brightgreen.svg)](https://behavedrift-api.onrender.com/docs)

---

### 🚀 Try it now — [Live API Demo](https://behavedrift-api.onrender.com/docs)

| Resource | URL |
|----------|-----|
| **Interactive Swagger UI** | [behavedrift-api.onrender.com/docs](https://behavedrift-api.onrender.com/docs) |
| **ReDoc API Reference** | [behavedrift-api.onrender.com/redoc](https://behavedrift-api.onrender.com/redoc) |
| **Health Check** | [behavedrift-api.onrender.com/health](https://behavedrift-api.onrender.com/health) |

> *Free-tier hosting — first request after inactivity may take ~30 seconds to wake up.*

---

> **BehaveDrift API** is an open-source, REST-based AI engine that continuously analyses longitudinal behavioural, physiological, and care observation data for residents living with dementia or cognitive decline. It detects subtle deviations from each resident's **personal baseline** — flagging early warning signs of infections (UTIs, respiratory), psychological decline, or medication side effects **before they escalate** into clinical emergencies.

> Designed natively for care-tech platforms such as **[Nourish](https://nourishcare.com)**, **[Radar Healthcare](https://radarhealthcare.com)**, **[Person Centred Software](https://personcentredsoftware.com)**, **[Access Care Planning](https://www.theaccessgroup.com)** and any Digital Social Care Record (DSCR) system.

---

## 📌 Table of Contents

- [The Problem](#-the-problem)
- [Why This Matters](#-why-this-matters)
- [What BehaveDrift Detects](#-what-behavedrift-detects)
- [Core Features](#-core-features)
- [Architecture Overview](#-architecture-overview)
- [API Reference](#-api-reference)
  - [Authentication](#authentication)
  - [Endpoints](#endpoints)
  - [Request & Response Examples](#request--response-examples)
- [Integration Guide](#-integration-guide)
  - [Nourish Integration](#nourish-integration)
  - [Radar Healthcare Integration](#radar-healthcare-integration)
  - [FHIR R4 Integration](#fhir-r4-integration)
  - [Webhook Events](#webhook-events)
- [AI Model & Data Science](#-ai-model--data-science)
- [Getting Started](#-getting-started)
- [Configuration](#-configuration)
- [Security & Compliance](#-security--compliance)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🔍 The Problem

Residents living with dementia cannot reliably self-report pain, discomfort, or illness. The most common early indicators — changes in sleep, agitation, appetite, social withdrawal, restlessness, and confusion — are **subtle, gradual and invisible to existing point-in-time care recording tools**.

Current platforms used across the UK care sector excel at:
- Documenting care interactions (Nourish, Person Centred Software)
- Logging incidents and compliance audits (Radar Healthcare)
- Medication administration (eMAR systems)

**But none offer:**
- ❌ Continuous, resident-specific behavioural baseline modelling
- ❌ Proactive drift detection across multi-week longitudinal windows
- ❌ Clinical correlation to infection markers (UTI, respiratory)
- ❌ Open, interoperable API for third-party care platforms to consume

The consequence is that **UTIs alone account for 30–40% of hospital admissions among care home residents** (NHS England, 2023), the majority of which are identified too late.

---

## 💡 Why This Matters

| Metric | Impact |
|--------|--------|
| UTI-related emergency admissions from care homes | ~80,000/year (NHS England) |
| Average cost per avoidable hospital admission | £3,500–£7,000 |
| Proportion of dementia residents with UTIs who show NO classic symptoms | ~60% |
| Early detection window for behavioural UTI signals | 3–7 days before clinical presentation |
| Reduction in hospitalisations with proactive monitoring (studies) | 20–35% |

**BehaveDrift API** closes this gap by turning the rich longitudinal data already captured in care records into a **proactive early warning system**.

---

## 🎯 What BehaveDrift Detects

### 🔴 Infection Indicators (UTI, Respiratory, Sepsis Precursors)
- Sudden increase in agitation or aggression (new baseline)
- Unexplained decline in appetite or fluid intake
- Increased confusion or disorientation beyond personal norm
- Sleep fragmentation (night-time disturbances increasing)
- Reduced mobility or withdrawal from usual activities

### 🟡 Psychological Drift
- Progressive mood decline over 2–4 week windows
- Social withdrawal pattern changes
- Increased repetitive behaviours or vocalisation
- Sundowning pattern shifts (evening agitation onset changes)

### 🟢 Positive Drift (Improvement Signals)
- Sustained mood improvements following care plan changes
- Increased engagement and activity participation
- Stabilisation after medication adjustments

### ⚪ Medication & Environmental Correlations
- Post-medication-change behavioural shifts
- Seasonal or environmental trigger correlations
- Staffing continuity correlation with resident stability

---

## ⚙️ Core Features

### 1. 🏗️ Resident Baseline Profiling
- Automatically constructs a **personal behavioural baseline** per resident using a configurable rolling window (default: 28 days)
- Adapts baseline dynamically to account for disease progression
- Supports multi-dimensional signals: mood, behaviour, sleep, appetite, mobility, pain indicators, social engagement

### 2. 📉 Drift Detection Engine
- **Statistical drift scoring** using Z-score deviation + CUSUM (Cumulative Sum Control) algorithms
- **Temporal pattern matching** — detects gradual shifts missed by point-in-time assessments
- **Multi-signal fusion** — correlates multiple concurrent weak signals into a single high-confidence alert
- Configurable **alert thresholds** per care setting and resident risk profile

### 3. 🚨 Tiered Alert System

| Tier | Name | Meaning | Recommended Action |
|------|------|---------|-------------------|
| T1 | Watch | Early weak signal(s) detected | Log & monitor |
| T2 | Concern | Sustained drift across 2+ signals | Notify key worker |
| T3 | Alert | High-confidence clinical correlation | Notify RN / GP |
| T4 | Critical | Severe & rapid multi-signal deviation | Immediate escalation |

### 4. 🔗 Interoperability-First Design
- **FHIR R4** native observation schema support
- **Webhook push** events for real-time platform integration
- **RESTful JSON API** with OpenAPI 3.1 specification
- Standard **HL7 FHIR Condition** resources for clinical handover
- **SNOMED CT** coded observations

### 5. 📊 Longitudinal Analytics Dashboard API
- Query aggregated drift trends across a care home
- Population-level heat maps of risk distribution
- Staff shift correlation analysis
- Export-ready reports (PDF, CSV, FHIR Bundle)

### 6. 🧩 Explainability & Transparency
- **Every alert includes a natural-language explanation** of the contributing signals
- Confidence score (0.0–1.0) with signal breakdown
- Historical context shown alongside the alert
- Designed for frontline carers — not just clinicians

### 7. 🔒 Privacy-Preserving by Design
- Fully **pseudonymised** resident identifiers  
- Data **never leaves your tenancy** unless explicitly configured
- On-premise or cloud-hosted deployment options
- UK ICO compliant, GDPR Article 25 (Privacy by Design)

---

## 🏛️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Care Platform Layer                          │
│   Nourish    │   Radar Healthcare   │   PCS   │   Custom DSCR      │
└──────────────┬──────────────────────┬─────────┬────────────────────┘
               │  REST / Webhook      │         │
               ▼                      ▼         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     BehaveDrift API Gateway                         │
│            Authentication  │  Rate Limiting  │  Tenant Isolation   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
               ┌─────────────▼─────────────┐
               │    Ingestion Service       │
               │  Normalise → Validate →   │
               │  FHIR Observation Map     │
               └─────────────┬─────────────┘
                             │
               ┌─────────────▼─────────────┐
               │   Baseline Engine          │
               │  Rolling Window Profiler  │
               │  Per-Resident Model Store │
               └─────────────┬─────────────┘
                             │
               ┌─────────────▼─────────────┐
               │   Drift Detection Engine   │
               │  CUSUM + Z-Score Analysis │
               │  Multi-Signal Fusion       │
               │  Infection Pattern Lib    │
               └─────────────┬─────────────┘
                             │
          ┌──────────────────▼──────────────────┐
          │          Alert & Event Bus           │
          │   Tier Classification │ Explainer   │
          │   Webhook Dispatch  │ API Response  │
          └──────────────────────────────────────┘
```

### Technology Stack (Reference Implementation)

| Layer | Technology |
|-------|-----------|
| API Framework | Python / FastAPI |
| ML / Statistics | scikit-learn, statsmodels, Prophet |
| Data Store | PostgreSQL (time-series extensions) |
| Message Bus | Redis Streams / RabbitMQ |
| FHIR Server | HAPI FHIR (optional) |
| Auth | OAuth 2.0 + JWT |
| Deployment | Docker / Kubernetes |
| API Docs | OpenAPI 3.1 / Swagger UI |

---

## 📡 API Reference

### Authentication

All API requests must include a Bearer token obtained via OAuth 2.0 client credentials flow.

```http
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id=YOUR_CLIENT_ID
&client_secret=YOUR_CLIENT_SECRET
&scope=behavedrift:read behavedrift:write
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "behavedrift:read behavedrift:write"
}
```

All subsequent requests:
```http
Authorization: Bearer <access_token>
X-Tenant-ID: your-organisation-id
```

---

### Endpoints

#### Observations (Data Ingestion)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/v1/observations` | Submit a single behavioural observation |
| `POST` | `/v1/observations/batch` | Submit a batch of observations |
| `GET` | `/v1/observations/{resident_id}` | Retrieve observation history |
| `POST` | `/v1/observations/fhir` | Submit FHIR R4 Observation resource |

#### Residents

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/v1/residents` | Register a new resident |
| `GET` | `/v1/residents/{resident_id}` | Get resident profile & baseline summary |
| `PUT` | `/v1/residents/{resident_id}/baseline/reset` | Manually reset baseline (e.g., post-hospitalisation) |
| `GET` | `/v1/residents/{resident_id}/baseline` | Get current baseline model |

#### Drift & Alerts

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/alerts` | Get all active alerts for the tenant |
| `GET` | `/v1/alerts/{resident_id}` | Get alerts for a specific resident |
| `GET` | `/v1/alerts/{alert_id}` | Get detailed alert with explanation |
| `POST` | `/v1/alerts/{alert_id}/acknowledge` | Acknowledge and log action taken |
| `DELETE` | `/v1/alerts/{alert_id}` | Dismiss an alert with reason |

#### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/analytics/population` | Population-level risk distribution |
| `GET` | `/v1/analytics/trends/{resident_id}` | Longitudinal trend data per resident |
| `GET` | `/v1/analytics/correlations` | Staff / environment correlation analysis |
| `GET` | `/v1/analytics/export` | Export report (PDF, CSV, FHIR Bundle) |

#### Webhooks

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/v1/webhooks` | Register a webhook endpoint |
| `GET` | `/v1/webhooks` | List registered webhooks |
| `DELETE` | `/v1/webhooks/{webhook_id}` | Remove a webhook |

---

### Request & Response Examples

#### Submit a Behavioural Observation

```http
POST /v1/observations
Authorization: Bearer {token}
Content-Type: application/json

{
  "resident_id": "res_7f3a9c21",
  "observed_at": "2025-06-12T14:30:00Z",
  "observer_id": "staff_42b",
  "signals": {
    "mood": {
      "value": 2,
      "scale": "1-5",
      "notes": "Noticeably more agitated than usual this afternoon"
    },
    "appetite": {
      "value": "poor",
      "enum": ["excellent", "good", "fair", "poor", "refused"],
      "meal": "lunch",
      "fluid_intake_ml": 120
    },
    "sleep_quality": {
      "value": "disturbed",
      "night_wakings": 4
    },
    "social_engagement": {
      "value": "withdrawn",
      "activity_participated": false
    },
    "pain_indicators": {
      "facial_grimacing": false,
      "guarding": false,
      "vocalisation": true
    },
    "mobility": {
      "value": "reduced",
      "baseline_comparison": "worse_than_usual"
    }
  },
  "context": {
    "location": "lounge",
    "visitor_present": false,
    "medication_administered": true,
    "medication_notes": "Routine morning meds given"
  }
}
```

**Response:**
```json
{
  "observation_id": "obs_a9d2f1c3",
  "resident_id": "res_7f3a9c21",
  "processed_at": "2025-06-12T14:30:04Z",
  "drift_evaluation": {
    "triggered": true,
    "drift_score": 0.67,
    "signals_flagged": ["mood", "appetite", "social_engagement"],
    "alert_generated": {
      "alert_id": "alr_3c8e1b90",
      "tier": "T2",
      "tier_label": "Concern"
    }
  },
  "status": "processed"
}
```

#### Retrieve a Detailed Alert

```http
GET /v1/alerts/alr_3c8e1b90
Authorization: Bearer {token}
```

**Response:**
```json
{
  "alert_id": "alr_3c8e1b90",
  "resident_id": "res_7f3a9c21",
  "resident_name": "Margaret [Pseudonymised]",
  "generated_at": "2025-06-12T14:30:04Z",
  "tier": "T2",
  "tier_label": "Concern",
  "confidence_score": 0.74,
  "drift_score": 0.67,
  "explanation": {
    "summary": "Margaret is showing a sustained pattern change across 3 signals over the past 72 hours. Her mood score is 1.8 standard deviations below her 28-day baseline. Combined with reduced appetite and social withdrawal, this pattern is consistent with early-stage infection indicators observed in her historical record.",
    "signals": [
      {
        "signal": "mood",
        "current_value": 2,
        "baseline_mean": 3.7,
        "baseline_std": 0.6,
        "z_score": -2.83,
        "deviation_days": 3
      },
      {
        "signal": "appetite",
        "current_value": "poor",
        "baseline_most_common": "good",
        "deviation_days": 2
      },
      {
        "signal": "social_engagement",
        "current_value": "withdrawn",
        "baseline_most_common": "engaged",
        "deviation_days": 3
      }
    ],
    "clinical_correlation": {
      "pattern": "early_infection_indicator",
      "confidence": 0.63,
      "suggested_actions": [
        "Check fluid intake over past 48 hours",
        "Observe for additional UTI indicators (increased confusion, malodorous urine, pain on movement)",
        "Consider requesting urine dipstick test",
        "Notify responsible clinical lead"
      ]
    }
  },
  "historical_context": {
    "previous_uti_episode": "2024-11-03",
    "pre_uti_pattern_match_score": 0.81
  },
  "metadata": {
    "acknowledged": false,
    "acknowledged_by": null,
    "action_taken": null
  }
}
```

#### Population Risk Overview

```http
GET /v1/analytics/population?location=main_building&date=2025-06-12
Authorization: Bearer {token}
```

**Response:**
```json
{
  "generated_at": "2025-06-12T16:00:00Z",
  "location": "main_building",
  "total_residents": 42,
  "risk_distribution": {
    "stable": 31,
    "watch_t1": 6,
    "concern_t2": 4,
    "alert_t3": 1,
    "critical_t4": 0
  },
  "trending_signals": ["mood", "sleep_quality"],
  "active_alerts": [
    {
      "resident_id": "res_7f3a9c21",
      "tier": "T2",
      "primary_signals": ["mood", "appetite", "social_engagement"]
    },
    {
      "resident_id": "res_2b1d4e88",
      "tier": "T3",
      "primary_signals": ["agitation", "sleep_quality", "fluid_intake"]
    }
  ]
}
```

---

## 🔌 Integration Guide

### Nourish Integration

BehaveDrift integrates with Nourish via its **Integration Hub API** and **Webhook** capabilities.

**Step 1: Configure Nourish Outbound Webhooks**

In your Nourish tenant, navigate to **Settings → Integration Hub** and register BehaveDrift as a webhook receiver for the following care record events:

- `care.observation.mood_recorded`
- `care.observation.food_fluid_recorded`
- `care.observation.sleep_recorded`
- `care.observation.activity_recorded`
- `care.observation.behaviour_recorded`

**Step 2: Map Nourish Observation Types to BehaveDrift Signals**

```json
{
  "nourish_signal_map": {
    "wellbeing_score": "mood",
    "food_intake_percentage": "appetite",
    "fluid_intake_ml": "fluid_intake_ml",
    "sleep_hours": "sleep_quality",
    "activity_participation": "social_engagement",
    "behaviour_concern": "agitation"
  }
}
```

**Step 3: Push Observations to BehaveDrift**

```python
import httpx

def on_nourish_care_record_event(event: dict):
    """Called by your Nourish webhook handler."""
    observation = map_nourish_to_behavedrift(event)
    
    response = httpx.post(
        "https://behavedrift-api.onrender.com/v1/observations",
        json=observation,
        headers={
            "Authorization": f"Bearer {BEHAVEDRIFT_TOKEN}",
            "X-Tenant-ID": YOUR_TENANT_ID
        }
    )
    response.raise_for_status()
    return response.json()
```

**Step 4: Receive Alerts Back into Nourish**

Register a BehaveDrift webhook pointing to your Nourish integration endpoint. BehaveDrift will POST alert events to your endpoint, which can then create Nourish handover notes, risk flags, or staff notifications programmatically.

---

### Radar Healthcare Integration

BehaveDrift complements Radar Healthcare's **Incident & Risk Management** workflows by providing the precursor intelligence that drives incident prevention.

**Integration Architecture:**

```
BehaveDrift Alert (T3/T4)
       ↓
Radar Healthcare API: POST /incidents
       ↓
Radar Investigation Workflow triggered
       ↓
Action Plan created with BehaveDrift context attached
```

**Radar Healthcare Webhook Handler (Example):**

```python
from radar_healthcare_sdk import RadarClient

radar = RadarClient(api_key=RADAR_API_KEY, org_id=RADAR_ORG_ID)

def on_behavedrift_alert(alert: dict):
    """Triggered when BehaveDrift sends a T3 or T4 alert."""
    if alert["tier"] in ["T3", "T4"]:
        radar.incidents.create({
            "title": f"Behavioural Alert – {alert['tier_label']}",
            "description": alert["explanation"]["summary"],
            "resident_ref": alert["resident_id"],
            "risk_level": "high" if alert["tier"] == "T4" else "medium",
            "source": "BehaveDrift API",
            "suggested_actions": alert["explanation"]["clinical_correlation"]["suggested_actions"],
            "created_at": alert["generated_at"]
        })
```

---

### FHIR R4 Integration

BehaveDrift supports native **FHIR R4 Observation** ingestion, enabling direct integration with any FHIR-compliant system, NHS SPINE-connected platforms, or hospital EPR systems.

**Submit an Observation as FHIR R4:**

```http
POST /v1/observations/fhir
Content-Type: application/fhir+json
Authorization: Bearer {token}

{
  "resourceType": "Observation",
  "status": "final",
  "category": [{
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/observation-category",
      "code": "survey"
    }]
  }],
  "code": {
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "285854004",
      "display": "Emotion (observable entity)"
    }]
  },
  "subject": {
    "reference": "Patient/res_7f3a9c21"
  },
  "effectiveDateTime": "2025-06-12T14:30:00Z",
  "valueInteger": 2
}
```

**Alerts as FHIR Condition Resources:**

BehaveDrift can output T3/T4 alerts as FHIR `Condition` resources for clinical handover:

```json
{
  "resourceType": "Condition",
  "clinicalStatus": {
    "coding": [{ "code": "active" }]
  },
  "category": [{
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "413350009",
      "display": "Finding related to risk factor management"
    }]
  }],
  "code": {
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "14880008",
      "display": "Behavioral finding (finding)"
    }]
  },
  "subject": { "reference": "Patient/res_7f3a9c21" },
  "onsetDateTime": "2025-06-12T14:30:00Z",
  "note": [{
    "text": "T2 Concern: Sustained mood, appetite and social withdrawal drift over 72hrs. Possible early infection indicator."
  }]
}
```

---

### Webhook Events

BehaveDrift publishes the following events to registered webhooks:

| Event | Trigger | Payload |
|-------|---------|---------|
| `alert.created` | New drift alert generated | Full alert object |
| `alert.tier_escalated` | Alert tier increases (T1→T2 etc.) | Alert with escalation context |
| `alert.acknowledged` | Staff acknowledges alert | Alert + acknowledgement metadata |
| `alert.resolved` | Alert dismissed or resolved | Alert + resolution notes |
| `baseline.updated` | Resident baseline recalculated | Summary of baseline changes |
| `resident.risk_status_changed` | Overall resident risk changes | Resident + new risk level |

**Webhook Payload Signature Verification:**

All webhooks are signed using HMAC-SHA256. Verify the signature:

```python
import hmac, hashlib

def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

---

## 🤖 AI Model & Data Science

### Baseline Construction
Each resident's baseline is modelled as a **multivariate time-series profile** using:
- **Rolling 28-day window** (configurable: 14, 28, 56, 90 days)
- **Weighted recency** — more recent observations carry more weight
- **Adaptive recalibration** — detects legitimate long-term progression vs acute drift

### Drift Detection Algorithms

| Algorithm | Use Case |
|-----------|----------|
| **CUSUM (Cumulative Sum)** | Detect gradual directional shifts |
| **Z-Score Deviation** | Detect acute outlier observations |
| **Isolation Forest** | Multivariate anomaly detection |
| **Prophet (Facebook)** | Temporal pattern & seasonality awareness |

### Infection Pattern Library
A curated library of **behavioural indicator patterns based on published clinical literature** — including [NICE CG161](https://www.nice.org.uk/guidance/cg161) (UTIs in adults), [NHS England dementia care guidance](https://www.england.nhs.uk/mental-health/dementia/), and peer-reviewed observational studies on behavioural indicators of infection in dementia populations — is used to correlate detected drift patterns with known pre-infection behavioural presentations.

These are **decision-support heuristics, not diagnostic tools**. The library is:
- Open for community contribution and clinical review
- Versioned and transparent — every pattern cites its source

### Model Transparency
- All drift scores include a **signal contribution breakdown**
- No black-box decisions — every alert is traceable to specific observations
- Clinicians can inspect the full observation trail behind any alert

---

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for source installation)
- PostgreSQL 15+

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/ummaruje/behavedrift-api.git
cd behavedrift-api

# Copy environment configuration
cp .env.example .env

# Edit .env with your configuration
nano .env

# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec api alembic upgrade head

# Create your first tenant and API credentials
docker-compose exec api python manage.py create-tenant \
  --name "Sunrise Care Home" \
  --contact-email "admin@sunrisecare.co.uk"
```

**API is now running at:** `http://localhost:8000`  
**Interactive API Docs:** `http://localhost:8000/docs`  
**Health Check:** `http://localhost:8000/health`

### Source Installation

```bash
git clone https://github.com/ummaruje/behavedrift-api.git
cd behavedrift-api

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Run migrations (requires PostgreSQL running)
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## ⚙️ Configuration

Key environment variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/behavedrift

# Auth
JWT_SECRET_KEY=your-secure-secret-key
JWT_ALGORITHM=RS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Drift Engine
BASELINE_WINDOW_DAYS=28
DRIFT_ALERT_THRESHOLD_T1=0.40
DRIFT_ALERT_THRESHOLD_T2=0.60
DRIFT_ALERT_THRESHOLD_T3=0.75
DRIFT_ALERT_THRESHOLD_T4=0.90

# Webhooks
WEBHOOK_SIGNING_SECRET=your-webhook-secret
WEBHOOK_TIMEOUT_SECONDS=10
WEBHOOK_RETRY_ATTEMPTS=3

# FHIR Integration (optional)
FHIR_SERVER_URL=https://your-fhir-server.nhs.net/fhir
FHIR_AUTH_TOKEN=your-fhir-token

# Email Alerts (optional)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASS=your-sendgrid-key
ALERT_FROM_EMAIL=alerts@behavedrift.io

# Deployment
ENVIRONMENT=production
ALLOWED_HOSTS=behavedrift-api.onrender.com,localhost
```

---

## 🔒 Security & Compliance

### Data Security

| Control | Implementation |
|---------|---------------|
| Encryption at rest | Managed by database provider |
| Encryption in transit | TLS 1.3 |
| Authentication | OAuth 2.0 + JWT (RS256) |
| Authorisation | RBAC with tenant isolation |
| Audit logging | Standard relational audit table (app/models/audit.py) |
| Data residency | UK-hosted by default (AWS eu-west-2 / Azure UK South) |
| Pseudonymisation | Resident identifiers pseudonymised at ingestion |

### Compliance Frameworks

| Standard | Status |
|----------|--------|
| **GDPR / UK GDPR** | 🔧 Designed with Article 25 (Privacy by Design) principles — pseudonymised identifiers, tenant isolation, right to erasure endpoint |
| **NHS DSPT** | 🔄 Architecture supports DSPT alignment (toolkit not yet submitted) |
| **NHS Digital DSCR Standards** | 🔧 API designed for DSCR integration patterns |
| **CQC KLOE Data Requirements** | 🔧 Export formats designed to support CQC data requirements |
| **HL7 FHIR R4** | 🔧 Partial mapping — Observation, Patient, RiskAssessment resources |
| **SNOMED CT** | 🔧 Coded observations for supported signal types |

### Data Retention
- Observation data: Configurable retention (default 7 years, aligning with NHS records management)
- Alert logs: 7 years
- Audit logs: 10 years
- Anonymised analytics: Indefinite

### Right to Erasure
The API provides `/v1/residents/{resident_id}/gdpr/erase` endpoint to support UK GDPR Article 17 right to erasure requests, producing a verifiable deletion certificate.

---

## 🗺️ Roadmap

### v1.0.0 — Foundation *(Current)*
- [x] Core observation ingestion API
- [x] Resident baseline profiling
- [x] Z-score drift detection
- [x] Tiered alert system (T1–T4)
- [x] OAuth 2.0 + API Key dual authentication
- [x] Webhook event system
- [x] Tenant isolation and pseudonymised identifiers
- [x] Integration test suite
- [x] Docker deployment

### v1.1.0 — Clinical Enrichment *(Planned)*
- [ ] Expanded infection indicator pattern library (respiratory, cellulitis)
- [ ] PAINAD pain assessment signal integration
- [ ] Falls risk precursor correlation
- [ ] FHIR R4 observation input/output (currently partial mapping)
- [ ] GP-facing alert summary export

### v1.2.0 — AI Enhancement *(Exploring)*
- [ ] LLM-powered alert narrative generation
- [ ] Retrospective analysis: "Would BehaveDrift have caught this?" reporting
- [ ] Predictive risk scoring (7-day forward risk)
- [ ] Medication side-effect correlation engine

### v2.0.0 — Ecosystem *(Future Vision)*
- [ ] Real-time wearable data ingestion (vitals, activity sensors)
- [ ] Multi-resident cohort analysis (outbreak detection)
- [ ] Clinical system escalation integrations
- [ ] CUSUM algorithm alongside Z-score for gradual shift detection

---

## 🤝 Contributing

BehaveDrift is built for the care sector, by people who care. Contributions from engineers, clinical informaticists, data scientists, and care professionals are deeply welcome.

### Ways to Contribute

- 🐛 **Bug reports** — Open a GitHub issue
- 💡 **Feature requests** — Start a GitHub Discussion
- 🧪 **Clinical pattern library** — Submit pre-infection behavioural signatures from anonymised data
- 🔌 **Integration connectors** — Build and submit connectors for other care platforms
- 📖 **Documentation** — Improve guides and examples
- 🌍 **Translation** — Translate docs for non-English care settings

### Development Setup

```bash
# Fork and clone
git clone https://github.com/YOUR_FORK/behavedrift-api.git
cd behavedrift-api

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v --cov=app

# Run linting
ruff check app/
mypy app/
```

Please read [CONTRIBUTING.md](CONTRIBUTING.md) and our [Code of Conduct](CODE_OF_CONDUCT.md) before submitting pull requests.

---

## 📄 License

BehaveDrift API is released under the **MIT License**.

```
MIT License

Copyright (c) 2025 Umar Isa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 📬 Contact & Community

- **GitHub Discussions:** [github.com/umarisa/behavedrift-api/discussions](https://github.com/umarisa/behavedrift-api/discussions)
- **Email:** hello@behavedrift.io
- **Author:** [Umar Isa](https://github.com/umarisa) — AI Engineer, Care Sector Portfolio

---

<div align="center">

**Built with ❤️ for the 900,000 people living with dementia in the UK**

*"The most human thing we can do with AI is notice when someone needs us — before they can ask."*

</div>
