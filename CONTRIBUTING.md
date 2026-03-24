# Contributing to BehaveDrift API

Thank you for considering a contribution to BehaveDrift. This project exists to improve outcomes for people living with dementia — every contribution matters.

Please read this document fully before opening a pull request. Following these guidelines makes the review process faster for everyone.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Ways to Contribute](#ways-to-contribute)
- [Before You Start](#before-you-start)
- [Development Setup](#development-setup)
- [Branch Naming](#branch-naming)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Governance](#governance)
- [Clinical Pattern Contributions](#clinical-pattern-contributions)

---

## Code of Conduct

This project follows our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold it. Report unacceptable behaviour to `conduct@behavedrift.io`.

---

## Ways to Contribute

| Type | How |
|------|-----|
| 🐛 Bug Report | Open a GitHub Issue using the bug template |
| 💡 Feature Request | Open a GitHub Discussion first, then an issue if approved |
| 🔌 Integration Connector | Build a connector for a new care platform, submit a PR |
| 🧪 Clinical Pattern | Submit anonymised pre-infection behavioural signatures (see below) |
| 📖 Documentation | Fix, improve or translate any `.md` file or the OpenAPI spec |
| ✅ Tests | Add missing test coverage, especially integration tests |
| 🌍 Translation | Translate API error messages and alert explanations |

**Before contributing code**: open an issue or discussion first. This avoids duplicated effort and ensures your contribution aligns with the project roadmap.

---

## Before You Start

1. Check [open issues](https://github.com/umarisa/behavedrift-api/issues) and [open PRs](https://github.com/umarisa/behavedrift-api/pulls) to avoid duplication
2. For significant features, open a GitHub Discussion first and wait for maintainer feedback
3. For bug fixes, reference the related issue in your PR
4. For changes to the OpenAPI spec (`docs/openapi.yaml`), the spec must be updated *before* any implementation code

---

## Development Setup

```bash
# Fork the repository and clone your fork
git clone https://github.com/YOUR_USERNAME/behavedrift-api.git
cd behavedrift-api

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install all dependencies (including dev dependencies)
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copy environment config
cp .env.example .env

# Start development services (PostgreSQL, Redis)
docker-compose up -d db redis

# Run database migrations
make migrate

# Verify setup — run the test suite
make test

# Start the local development server
make dev
```

API is available at `http://localhost:8000`  
Interactive docs at `http://localhost:8000/docs`

---

## Branch Naming

Use the following convention:

```
<type>/<short-description>
```

| Type | When to use |
|------|------------|
| `feat/` | New feature or endpoint |
| `fix/` | Bug fix |
| `docs/` | Documentation only changes |
| `test/` | Adding or fixing tests |
| `refactor/` | Code change with no feature or fix |
| `chore/` | Dependency updates, CI changes, config |
| `perf/` | Performance improvements |

**Examples:**
```
feat/add-fhir-condition-output
fix/baseline-reset-missing-validation
docs/improve-nourish-integration-guide
test/add-drift-engine-unit-tests
```

---

## Commit Messages

This project uses [Conventional Commits](https://www.conventionalcommits.org/). This format enables automated changelog generation and semantic versioning.

**Format:**
```
<type>(<scope>): <short summary>

[optional body]

[optional footer: Fixes #123]
```

**Types:** `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `perf`, `ci`

**Examples:**
```
feat(drift-engine): add isolation forest multivariate anomaly detection

fix(auth): return 401 instead of 500 when JWT signature is invalid

docs(contributing): add clinical pattern contribution guide

test(observations): add integration tests for batch ingestion endpoint

Fixes #47
```

**Rules:**
- Summary line: 72 characters max, present tense, no period at end
- Body: explain *why*, not *what*
- Breaking changes: add `BREAKING CHANGE:` footer

---

## Pull Request Process

1. **Ensure your branch is up to date** with `main` before opening a PR
2. **Write or update tests** — PRs without tests for new functionality will not be merged
3. **Update the OpenAPI spec** if you change any endpoint, request schema, or response schema
4. **Update `CHANGELOG.md`** — add your change under `[Unreleased]`
5. **Update documentation** — if your change affects user-facing behaviour, update the relevant `.md` files
6. **Pass CI** — all checks must be green before review is requested
7. **Request review** — tag `@umarisa` or another maintainer

**PR Title:** Follow the same Conventional Commits format as your commit messages.

**PR Description must include:**
- What changed and why
- How to test the change manually
- Screenshots / curl examples if relevant
- Reference to the related issue (`Fixes #123`)

**Review SLA:** Maintainers aim to provide first feedback within 5 business days. Complex PRs may take longer.

---

## Coding Standards

### Python Style
- Formatter: **Black** (line length: 88)
- Linter: **Ruff**
- Type hints: **required** on all public functions and class methods
- Docstrings: **required** on all public functions (Google style)

Run before committing:
```bash
make lint    # ruff check + black --check
make format  # black + ruff --fix
```

### API Design Rules
- All new endpoints must be added to `docs/openapi.yaml` **first**
- All responses must use the standard error shape defined in `docs/adr/ADR-004-error-contract.md`
- All new endpoints must include auth (no unauthenticated endpoints except `/health` and `/docs`)
- Pagination is required for any endpoint that can return more than 20 records

### No Secrets in Code
- Never commit secrets, tokens, or credentials — use `.env` and `.env.example`
- The pre-commit hook will reject commits containing common secret patterns

---

## Testing Requirements

| Test Type | Minimum Requirement |
|-----------|-------------------|
| Unit tests | All business logic in `app/services/` must have unit tests |
| Integration tests | All endpoints must have at least one happy-path and one error-path integration test |
| Contract tests | Run automatically on CI via Schemathesis against the OpenAPI spec |
| Coverage threshold | 70% minimum on `app/` (excluding migrations) |

Run the full test suite:
```bash
make test           # unit + integration
make test-contract  # OpenAPI contract validation
make test-coverage  # coverage report
```

---

## Governance

**Who can merge PRs:** Currently `@umarisa` (sole maintainer). Additional maintainers will be added as the project grows — if you want to become a maintainer, open a Discussion.

**Breaking changes:** Require a GitHub Discussion with 5 business days for community input before being merged.

**Release cadence:** No fixed schedule for v1. Minor releases when enough features/fixes accumulate. Patch releases for security fixes: ASAP.

**Decision making:** Maintainer has final say on direction. Disagreements are resolved in GitHub Discussions, not in PR comments.

---

## Clinical Pattern Contributions

The infection pattern library (`app/patterns/`) defines the pre-clinical behavioural signatures used to correlate drift alerts with known infection presentations.

**To contribute a pattern:**
1. Pattern data must come from retrospective analysis of anonymised care records
2. Include a reference (study, clinical protocol, or care evidence source)
3. Include confidence and sample size metadata
4. Open a PR with the pattern definition file and accompanying unit tests
5. Pattern PRs will be reviewed by a clinical informaticist before merge

See `docs/clinical-patterns.md` for the pattern schema specification.

---

_Questions about contributing? Open a [GitHub Discussion](https://github.com/umarisa/behavedrift-api/discussions) — we're friendly._
