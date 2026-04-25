# BehaveDrift API: Comprehensive Overview

**Version:** 1.0.0
**Status:** Live / Core Foundation
**Target Audience:** Healthcare Platforms, DSCRs, Integration Engineers, Clinical Leads

---

## 1. Executive Summary & Problem Space

Currently, care technology systems excel at capturing point-in-time observational data but fail to perform longitudinal analysis on these records. As a result, critical early warning signals—subtle shifts in resident behavior, mood, appetite, and sleep—that reliably precede health deteriorations (such as UTIs, respiratory infections, or acute confusion episodes) are often missed until they emerge as clinical emergencies. 

**BehaveDrift API** addresses this gap. It is a REST-based AI engine that continuously analyses longitudinal care observation data. By establishing a resident's **personal behavioral baseline**, the API proactively flags deviations and anomalies 3 to 7 days before an emergency clinical presentation, converting passive care records into an active early warning system.

---

## 2. Core Capabilities & Detection Mechanisms

The API processes longitudinal data to detect three primary categories of behavioral pattern drift:

*   **🔴 Infection Indicators (UTI, Respiratory, Sepsis Precursors):** Unexplained appetite decline, sudden increases in agitation, disrupted sleep patterns, increased confusion, and reduced mobility.
*   **🟡 Psychological Drift:** Long-term sustained shifts such as progressive mood decline (over 2-4 weeks), social withdrawal, or changes to sundowning patterns.
*   **🟢 Positive Drift & Stabilization:** Improvements resulting from recent changes to care plans or environmental stabilization after medication adjustments.

A **Tiered Alert System (T1-T4)** translates the calculated drift anomalies into actionable alerts, mapping from early weak signals (`T1: Watch`) to rapid multi-signal deviations requiring immediate intervention (`T4: Critical`). Explainable AI provides a **natural-language explanation** for each alert, making it fully transparent to non-clinical care staff without "black-box" decision-making.

---

## 3. Architecture & Integration Points

BehaveDrift operates via a robust, highly-scalable, integration-first architecture designed to interoperate smoothly with care-tech vendors natively (such as Nourish, Access Care Planning, or Radar Healthcare):

1.  **Ingestion:** Natively supports custom JSON payloads and HL7 FHIR R4 Observations.
2.  **Baseline Engine:** Employs rolling profiling windows (default 28-days) that are dynamically adapted.
3.  **Analytics Layer:** Relies on CUSUM (Cumulative Sum Control) algorithms, Z-Score deviation profiling, and Temporal Pattern Matching to construct drift scores out of multivariate data points.
4.  **Webhooks & Callbacks:** Exposes a secure, real-time event-driven bus to actively push alert and baseline events to subscribing clients.

Key endpoints cover Data Ingestion (`/v1/observations`, `/v1/observations/fhir`), Resident Management (`/v1/residents`), Alert Consumption (`/v1/alerts`), and Population Trend Analytics (`/v1/analytics/population`). Authentication is managed securely via OAuth 2.0 with JWT.

---

## 4. Current System Limitations (v1.0.0 Boundaries)

To maintain focus, safety, and reliability in its v1.0 state, the system enforces intentional limitations. **BehaveDrift API currently does NOT:**

*   **Provide Diagnoses:** The engine produces *early warning signals* and statistical drift correlations, not definitive medical diagnoses. All outputs require review by a qualified clinical professional.
*   **Dictate Care Actions:** It does not control care plans, medication administration, or execute automated actions in the care platform. It provides read-only intelligence.
*   **Support Wearable or Real-time Vitals Streaming:** The v1.0 engine relies exclusively on intermittent care staff observations. Ingesting continuous high-frequency biometric streams is out-of-scope for the current implementation.
*   **Capture Audio/Video or Biometric Records:** BehaveDrift relies solely on quantified text and categorical observational data; rich media is not processed or stored.
*   **Support Resident Self-Reporting:** Feedback must be logged by observing staff, not independently via direct-to-resident input forms.
*   **Offer End-User Identity Management:** It functions as a Machine-to-Machine (M2M) API catering strictly to platforms, eliminating direct interactions with end users or carers.

---

## 5. Security & Compliance Posture

Designed inherently for the UK healthcare market, privacy and security are cornerstone priorities:

*   **Data Pseudonymization at Source:** The system is agnostic to true resident identity.
*   **Infrastructure Segregation:** Tenancy isolation implemented across REST endpoints.
*   **Encryption:** Transport secured via TLS 1.3, at-rest via database provider (e.g., Render Managed PostgreSQL).
*   **Compliance Status:** Prepared and aligned with **UK GDPR (Privacy by Design - Art.25)**, **NHS DSPT (Data Security & Protection Toolkit)**, and **CQC KLOE** reporting metrics.

---

## 6. Development & Future Roadmap 

While v1.0.0 lays the core foundation, future iterations are positioned to drastically enhance clinical utility and coverage:

*   **v1.1.0 – Clinical Enrichment (Upcoming):** Will introduce targeted precursor correlations specifically for falls risks and pain assessment scaling (e.g., PAINAD), as well as dedicated GP-facing alert clinical document exports.
*   **v1.2.0 – Enhancing GenAI Explainability:** Plans include incorporating Large Language Models (LLMs) to construct highly fluent, narrative-style insights for carers and retroactive "Would BehaveDrift have caught this?" audits.
*   **v2.0.0 – Wearable Ecosystem Integration:** Future capability expansions will move beyond observational points into accepting and analyzing high-frequency real-time vitals and sensor networks to trigger earlier deterioration flags.
