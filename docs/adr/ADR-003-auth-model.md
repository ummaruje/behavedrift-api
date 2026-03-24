# ADR-003: Authentication Model

**Date:** March 2026  
**Status:** Accepted  
**Author:** Umar Isa

---

## Context

BehaveDrift is a **machine-to-machine API** — it is not consumed directly by end users (carers, nurses). It is consumed by:
1. Care platform servers making server-side API calls
2. Self-hosted operators running their own backend services
3. Open source contributors building integration connectors

The auth model must be: secure enough for pseudonymised resident health data, simple enough for rapid integration by care-tech engineering teams, and standard enough to work with any HTTP client.

## Decision

**Dual auth model:**

| Mode | Mechanism | Use Case |
|------|-----------|----------|
| **Primary** | OAuth 2.0 Client Credentials + JWT (RS256) | Production SaaS integrations (Nourish, Radar Healthcare) |
| **Secondary** | API Key (header: `X-API-Key`) | Self-hosted deployments, development, simpler integrations |

Both modes are tenant-scoped — every credential is bound to a single tenant organisation.

## Rationale

**OAuth 2.0 Client Credentials** was chosen as the primary mode because:
- It is the industry standard for machine-to-machine auth
- Short-lived tokens (60 min) reduce the blast radius of credential compromise
- RS256 (asymmetric) signing means token verification can happen without database lookup
- Familiar to enterprise care-tech engineering teams
- Supported natively by most API gateways and integration platforms

**API Key** secondary mode is provided because:
- Many smaller care operators or individual contributors need a simple integration path
- OAuth2 adds setup friction for self-hosted deployments
- API keys are adequate when combined with HTTPS and rate limiting
- API keys are stored as bcrypt hashes — never in plaintext

**Session-based auth** was rejected: not appropriate for server-to-server API access.

**mTLS** was considered but rejected: adds significant client-side certificate management complexity that care-tech platforms are not set up for.

## Implementation

```
Tenant creation → Generate client_id + client_secret
                → Store client_secret as bcrypt hash
                → Never return secret after initial provisioning

Token request → Verify client_id + client_secret
            → Issue signed JWT (RS256, 60 min TTL)
            → Include tenant_id + scopes in claims

API request → Verify JWT signature (public key, no DB lookup)
           → Extract tenant_id from claims
           → Scope all database queries to tenant_id
```

## Scopes Defined

| Scope | Permission |
|-------|-----------|
| `behavedrift:read` | Read observations, alerts, analytics |
| `behavedrift:write` | Submit observations, acknowledge alerts |
| `behavedrift:admin` | Manage residents, webhooks, tenant config |

## Consequences

- All endpoints except `/health` and `/docs` require authentication
- Every database query must be scoped to `tenant_id` — this is enforced at the service layer, not the route layer
- JWT public keys are rotated on a defined schedule (quarterly in production)
- API keys have an optional expiry date and can be revoked individually
