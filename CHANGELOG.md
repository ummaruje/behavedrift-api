# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Initial project structure and documentation
- Problem statement, architecture decisions, and OpenAPI 3.1 spec
- CONTRIBUTING.md, SECURITY.md, CODE_OF_CONDUCT.md
- GitHub Actions CI pipeline
- Docker Compose configuration for local development

---

## [1.0.0] — Planned

### Added
- Core observation ingestion endpoint (`POST /v1/observations`)
- Batch observation ingestion (`POST /v1/observations/batch`)
- FHIR R4 Observation input/output support
- Resident baseline profiling with rolling 28-day window
- CUSUM + Z-score drift detection engine
- Tiered alert system (T1 Watch → T4 Critical) with natural-language explanations
- Infection pattern library: UTI and respiratory precursor signatures
- OAuth 2.0 + JWT authentication (RS256)
- API Key auth mode for simpler integrations
- Webhook event system for real-time platform integration
- Population-level analytics dashboard endpoints
- Docker and Docker Compose deployment
- OpenAPI 3.1 specification with Swagger UI
- Nourish integration guide
- Radar Healthcare integration guide
- GDPR erasure endpoint (`DELETE /v1/residents/{id}/gdpr/erase`)

---

## How This Changelog is Maintained

- Entries are written by contributors as part of every pull request
- The **[Unreleased]** section accumulates changes until a release is tagged
- Releases are tagged using `git tag v1.x.x` and the changelog entry is dated
- Automated release notes supplement (but do not replace) this file

[Unreleased]: https://github.com/umarisa/behavedrift-api/compare/HEAD
[1.0.0]: https://github.com/umarisa/behavedrift-api/releases/tag/v1.0.0
