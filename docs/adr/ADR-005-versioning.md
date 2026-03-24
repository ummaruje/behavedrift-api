# ADR-005: API Versioning Strategy

**Date:** March 2026  
**Status:** Accepted  
**Author:** Umar Isa

---

## Context

BehaveDrift will be integrated into production care management systems. Breaking API changes must be managed carefully — a silent breaking change in a care platform integration could cause alerts to stop firing or data to be silently dropped.

## Decision

**URL-based versioning** with a major version prefix on all endpoints.

```
/v1/observations
/v1/residents/{id}/alerts
/v1/analytics/population
```

## Rationale

Three strategies were considered:

| Strategy | Pros | Cons |
|----------|------|------|
| **URL versioning** (`/v1/`) | Simple, visible, cacheable, easy to route | URL changes on major version |
| **Header versioning** (`API-Version: 1`) | Clean URLs | Less visible, harder to test in browser, harder to cache |
| **Query param** (`?version=1`) | Easy to test | Not RESTful, easily forgotten |

**URL versioning** was chosen because:
- It is the most widely understood approach in the industry
- The version is immediately visible in logs, browser history, and API gateway routes
- Care-tech platform engineers can test endpoints directly in a browser
- It is simple to route different versions to different application instances
- FHIR itself uses URL-based versioning (`/fhir/R4/`)

## Versioning Rules

### What constitutes a MAJOR version bump (`v1` → `v2`)?
- Removing an endpoint
- Removing or renaming a required request field
- Changing the type of an existing field
- Changing authentication scheme
- Removing a previously documented error code

### What does NOT require a version bump?
- Adding a new optional request field
- Adding a new response field
- Adding a new endpoint
- Adding a new optional query parameter
- Bug fixes that correct documented behaviour

### Deprecation Process
1. Announce deprecation in `CHANGELOG.md` and via webhook event `api.version_deprecated`
2. Add `Deprecation` and `Sunset` headers to deprecated version responses
3. Maintain the deprecated version for a minimum of **12 months** from announcement
4. Remove after the sunset date

## Consequences

- All routes are prefixed with `/v1/` from day one — retrofitting this later is painful
- The OpenAPI spec is versioned alongside the code (one spec file per major version)
- Breaking changes require a discussion and go through the deprecation process above
- Minor/patch changes update the same spec and changelog without a new version prefix
