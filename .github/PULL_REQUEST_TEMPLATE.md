## Pull Request Summary

<!-- A clear, one-paragraph description of what this PR does and why. -->

**Type of change:**
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that causes existing functionality to change)
- [ ] Documentation update
- [ ] Refactor (no behaviour change)
- [ ] CI / DevOps change
- [ ] Dependency update

Closes: #<!-- issue number -->

---

## OpenAPI Spec

- [ ] This PR does NOT change any endpoints, request schemas, or response schemas
- [ ] This PR changes the API — `docs/openapi.yaml` has been updated **before** any implementation code

---

## Changes Made

<!-- List the specific files changed and what was done. Be concise. -->

- `app/services/drift_engine.py` — Added isolation forest multivariate detection
- `docs/openapi.yaml` — Added `drift_method` field to observation response
- `tests/unit/test_drift_engine.py` — Unit tests for new detection method

---

## Testing

**How to test this change manually:**

```bash
# Example curl or make command to reproduce/verify
make test
```

**Test checklist:**
- [ ] Unit tests pass: `make test-unit`
- [ ] Integration tests pass: `make test-integration`
- [ ] Contract tests pass: `make test-contract`
- [ ] Coverage is above 70%: `make test-coverage`
- [ ] Linting passes: `make lint`

---

## Checklist

- [ ] My code follows the coding standards in [CONTRIBUTING.md](CONTRIBUTING.md)
- [ ] I have written or updated tests for my changes
- [ ] I have updated `CHANGELOG.md` under `[Unreleased]`
- [ ] I have updated documentation if behaviour changed
- [ ] No secrets, PII, or real resident data appears anywhere in this PR
- [ ] I have tested this against a real (local) database, not mocks only

---

## Screenshots / Evidence
<!-- For endpoint changes, include curl example with response. For drift engine changes, include before/after alert scores. -->
