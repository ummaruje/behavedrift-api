# ADR-002: Technology Stack

**Date:** March 2026  
**Status:** Accepted  
**Author:** Umar Isa

---

## Context

The stack must be: familiar enough for open source contributors to onboard quickly, production-grade, and well-suited to time-series data processing and ML inference.

## Decision

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Language** | Python 3.11+ | Largest data science / ML ecosystem; familiar to care-tech engineers; strong async support |
| **API Framework** | FastAPI | Async-native, auto-generates OpenAPI docs, excellent type safety via Pydantic, fast performance |
| **Data Validation** | Pydantic v2 | Strict schema validation, native JSON serialisation, integrates with FastAPI |
| **Database** | PostgreSQL 15+ | Best-in-class time-series support via TimescaleDB extension; ACID compliant; open source |
| **ORM / Migrations** | SQLAlchemy + Alembic | Industry standard; contributor-familiar; supports async; Alembic handles schema migrations |
| **Message Queue** | Redis Streams | Lightweight; used for webhook delivery queue and rate limiting; familiar to most engineers |
| **ML / Statistics** | scikit-learn + statsmodels + Prophet | Well-documented, contributor-friendly, no proprietary dependencies |
| **Auth** | python-jose + passlib | JWT handling; RS256 support; well-maintained |
| **Testing** | pytest + httpx | Standard Python testing; httpx for async API client in integration tests |
| **Linting** | Ruff + Black + mypy | Fast, modern Python tooling; enforced by pre-commit hooks |
| **Container** | Docker + Docker Compose | Universal deployment; minimises local setup friction for contributors |

## Alternatives Rejected

- **Node.js/Express** — Python's ML ecosystem is significantly superior; important for the drift detection engine
- **Django REST Framework** — heavier than needed; slower auto-documentation; less suited to async workloads
- **FastAPI + MongoDB** — document databases are less suited to structured time-series observation data; harder to query across time windows efficiently
- **Rust/Axum** — too high a barrier for open source contributors; no material performance benefit at the expected scale

## Consequences

- All contributors must be comfortable with Python 3.11+
- The `requirements.txt` is pinned to exact versions for reproducibility
- `requirements-dev.txt` contains development-only dependencies (pytest, ruff, black, mypy, schemathesis)
- TimescaleDB is an optional enhancement — the API works with plain PostgreSQL out of the box
