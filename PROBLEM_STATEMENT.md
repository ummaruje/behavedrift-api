# BehaveDrift API — Problem Statement

**Version:** 1.0  
**Date:** March 2026  
**Author:** Umar Isa  
**Status:** Approved

---

## What This API Does

BehaveDrift API is a **REST-based AI inference engine** that accepts longitudinal care observation data (mood, appetite, sleep, mobility, social engagement, pain indicators) for individual dementia residents and returns:

1. A **drift score** quantifying deviation from that resident's personal behavioural baseline
2. **Tiered alerts** (T1–T4) when drift patterns match known pre-clinical deterioration signatures
3. **Natural-language explanations** of the contributing signals, suitable for frontline care staff
4. **FHIR R4 Condition resources** for clinical handover to GPs and NHS systems

---

## Who Uses This API

| Consumer | Use Case |
|----------|----------|
| **Care management platforms** (Nourish, Person Centred Software, Access Care Planning) | Embed drift alerts into their existing care record workflows |
| **Quality & compliance platforms** (Radar Healthcare) | Receive T3/T4 alerts as pre-populated incident records |
| **NHS-connected systems** | Consume FHIR R4 outputs for clinical escalation workflows |
| **Care home operators (self-hosted)** | Run the API independently alongside any care software |
| **Researchers & academics** | Access anonymised population-level drift analytics |

---

## What This API Does NOT Do

This boundary exists to keep the API focused, reliable, and safe:

- ❌ **Does not diagnose medical conditions.** BehaveDrift produces *early warning signals*, not diagnoses. No output constitutes clinical advice.
- ❌ **Does not replace clinical judgement.** All T3/T4 alerts require review by a qualified clinician before action.
- ❌ **Does not control care plans or medication.** It produces read-only intelligence; care actions are taken in the care platform.
- ❌ **Does not ingest real-time vitals or wearable device streams** (planned for v2.0 — out of scope for v1).
- ❌ **Does not manage resident identity or authentication** for end users — it is a machine-to-machine API consumed by platforms, not directly by carers.
- ❌ **Does not store video, audio, or biometric data.**
- ❌ **Does not support self-reporting by residents** — all input is care staff observations.

---

## Problem it Solves (In One Paragraph)

Residents living with dementia cannot reliably self-report pain or illness. Existing care technology captures observations as discrete point-in-time records but performs no longitudinal analysis across those records. The result is that early warning signals — subtle shifts in mood, appetite, sleep, and engagement that reliably precede UTIs, respiratory infections, and acute confusion episodes — go undetected until a medical crisis occurs. BehaveDrift converts the observation data already captured by care platforms into a proactive, resident-specific early warning system that flags deterioration 3–7 days before clinical presentation.

---

## Success Criteria for v1.0

- A care platform can submit an observation and receive a drift score in < 500ms
- Alerts are generated with a natural-language explanation that a non-clinical carer can act on
- The API is deployable by a single engineer in < 30 minutes using Docker
- The OpenAPI spec and implementation are kept in sync (contract tested on CI)
- Zero personally identifiable information appears in logs
