# ADR-001: API Style — REST

**Date:** March 2026  
**Status:** Accepted  
**Author:** Umar Isa

---

## Context

BehaveDrift API needs to be consumed by:
- Care management platforms (SaaS products with engineering teams)
- NHS-connected clinical systems
- Individual care home operators deploying self-hosted instances
- Open source contributors building integration connectors

Three options were considered: REST, GraphQL, and gRPC.

## Decision

**REST over HTTP/JSON** using OpenAPI 3.1 as the specification standard.

## Rationale

| Factor | REST | GraphQL | gRPC |
|--------|------|---------|------|
| Industry familiarity | ✅ Universal | ⚠️ Growing | ❌ Limited |
| Care tech platform support | ✅ All platforms | ⚠️ Varies | ❌ Poor |
| API tooling ecosystem | ✅ Excellent | ✅ Good | ⚠️ Limited |
| Documentation tooling | ✅ Swagger/Redoc | ✅ GraphiQL | ❌ Poor |
| Contributor accessibility | ✅ High | ⚠️ Medium | ❌ Low |
| Browser support | ✅ Native | ✅ Native | ❌ Requires proxy |
| FHIR alignment | ✅ FHIR is REST-native | ❌ Non-standard | ❌ Non-standard |

**GraphQL** was rejected because: the query flexibility it provides is unnecessary for the well-defined, structured observation data BehaveDrift handles; it adds significant complexity for contributors; and the target consumer platforms (Nourish, Radar Healthcare) use REST-native integration hubs.

**gRPC** was rejected because: it has poor browser support, requires generated client code, is unfamiliar to most care-tech engineering teams, and adds unnecessary complexity for a public-facing API.

## Consequences

- All endpoints use HTTP verbs (GET, POST, PUT, DELETE) with JSON request/response bodies
- The OpenAPI 3.1 spec in `docs/openapi.yaml` is the single source of truth
- Code is generated from the spec (spec-first), not the spec from code
- Contract testing via Schemathesis validates spec-implementation alignment on every PR
