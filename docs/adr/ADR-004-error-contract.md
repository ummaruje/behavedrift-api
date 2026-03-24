# ADR-004: Error Response Contract

**Date:** March 2026  
**Status:** Accepted  
**Author:** Umar Isa

---

## Context

Inconsistent error responses are the most common complaint against open source APIs. Care platform engineers integrating BehaveDrift need predictable, machine-parseable errors across every endpoint.

## Decision

All error responses use a single, consistent structure:

```json
{
  "error": "validation_error",
  "message": "Field 'resident_id' is required and cannot be blank.",
  "code": 422,
  "details": [
    {
      "field": "resident_id",
      "issue": "required",
      "value": null
    }
  ],
  "request_id": "req_4f3a9c21d",
  "documentation_url": "https://docs.behavedrift.io/errors/validation_error"
}
```

| Field | Type | Always Present | Description |
|-------|------|----------------|-------------|
| `error` | string | ✅ | Machine-readable error code (snake_case) |
| `message` | string | ✅ | Human-readable explanation |
| `code` | integer | ✅ | HTTP status code |
| `details` | array | ❌ | Field-level validation errors (422 only) |
| `request_id` | string | ✅ | Unique ID for log correlation |
| `documentation_url` | string | ❌ | Link to error docs (where applicable) |

## Standard Error Codes

| error | HTTP Status | When Used |
|-------|-------------|-----------|
| `authentication_required` | 401 | Missing or expired token |
| `invalid_credentials` | 401 | Invalid client_id/secret |
| `forbidden` | 403 | Valid auth but insufficient scope |
| `not_found` | 404 | Resource does not exist (or belongs to another tenant) |
| `validation_error` | 422 | Request body fails schema validation |
| `rate_limit_exceeded` | 429 | Too many requests |
| `conflict` | 409 | Duplicate resource (e.g., resident already registered) |
| `baseline_insufficient` | 422 | Resident has too few observations for drift analysis |
| `internal_error` | 500 | Unexpected server error |
| `service_unavailable` | 503 | Temporary outage or maintenance |

## Tenant Isolation Rule

A request for a resource that exists but belongs to another tenant returns `404 not_found` — **never** `403 forbidden`. This prevents information leakage about other tenants' data.

## Consequences

- A shared `ErrorResponse` Pydantic model is used across all route handlers
- FastAPI exception handlers map all exceptions to this structure
- The `request_id` is generated at the middleware layer and included in response headers (`X-Request-ID`) and logs
- The OpenAPI spec documents all possible error responses for every endpoint
