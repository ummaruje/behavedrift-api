# BehaveDrift API — Makefile
# Run `make help` to see all available commands

.PHONY: help dev build test test-coverage test-contract lint format \
        migrate migrate-test clean docker-up docker-down docker-logs \
        generate-keys openapi-validate

# Detect Python command
PYTHON := python3
PIP := pip3
UVICORN := uvicorn

# ============================================================
# Help
# ============================================================

help: ## Show this help message
	@echo ""
	@echo "  BehaveDrift API — Development Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ============================================================
# Development
# ============================================================

dev: ## Start the development server with hot reload
	$(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000

build: ## Install all dependencies
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt

# ============================================================
# Database
# ============================================================

migrate: ## Run database migrations (development database)
	$(PYTHON) -m alembic upgrade head

migrate-test: ## Run database migrations (test database)
	DATABASE_URL=$(TEST_DATABASE_URL) $(PYTHON) -m alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create MSG="add resident table")
	$(PYTHON) -m alembic revision --autogenerate -m "$(MSG)"

migrate-rollback: ## Roll back the last migration
	$(PYTHON) -m alembic downgrade -1

# ============================================================
# Testing
# ============================================================

test: migrate-test ## Run unit and integration tests
	$(PYTHON) -m pytest tests/ -v --tb=short -x

test-unit: ## Run unit tests only
	$(PYTHON) -m pytest tests/unit/ -v --tb=short

test-integration: migrate-test ## Run integration tests only
	$(PYTHON) -m pytest tests/integration/ -v --tb=short

test-coverage: migrate-test ## Run tests with coverage report
	$(PYTHON) -m pytest tests/ -v --cov=app --cov-report=term-missing \
		--cov-report=html:htmlcov --cov-fail-under=70
	@echo "\n  Coverage report: htmlcov/index.html\n"

test-contract: ## Run OpenAPI contract tests against running server
	@echo "Validating OpenAPI spec against live server..."
	schemathesis run docs/openapi.yaml \
		--url http://localhost:8000 \
		--phases=fuzzing

test-load: ## Run basic load test (requires k6)
	k6 run tests/load/basic_load_test.js

# ============================================================
# Code Quality
# ============================================================

lint: ## Run linting checks (ruff + mypy)
	ruff check app/ tests/
	mypy app/ --ignore-missing-imports

format: ## Auto-format code (black + ruff --fix)
	black app/ tests/
	ruff check app/ tests/ --fix

format-check: ## Check formatting without modifying files (used by CI)
	black app/ tests/ --check
	ruff check app/ tests/

# ============================================================
# OpenAPI
# ============================================================

openapi-validate: ## Validate the OpenAPI specification
	$(PYTHON) -m openapi_spec_validator docs/openapi.yaml
	@echo "  ✅ OpenAPI spec is valid"

openapi-docs: ## Serve OpenAPI docs locally (requires redoc-cli)
	redoc-cli serve docs/openapi.yaml --port 8080
	@echo "  Docs available at: http://localhost:8080"

# ============================================================
# Docker
# ============================================================

docker-up: ## Start all services with Docker Compose
	docker-compose up -d

docker-dev: ## Start development services only (db + redis)
	docker-compose up -d db redis

docker-down: ## Stop all Docker services
	docker-compose down

docker-down-volumes: ## Stop all Docker services and remove data volumes
	docker-compose down -v

docker-logs: ## Follow logs from all services
	docker-compose logs -f

docker-build: ## Build the API Docker image
	docker build -t behavedrift-api:local .

# ============================================================
# Security
# ============================================================

generate-keys: ## Generate RSA key pair for JWT signing
	@mkdir -p keys
	@openssl genrsa -out keys/private.pem 2048
	@openssl rsa -in keys/private.pem -pubout -out keys/public.pem
	@chmod 600 keys/private.pem
	@echo "  ✅ Keys generated in ./keys/ — do not commit these files"

security-scan: ## Run security vulnerability scan
	bandit -r app/ -ll
	safety check -r requirements.txt

# ============================================================
# Clean
# ============================================================

clean: ## Remove build artifacts, caches, and temporary files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	@echo "  ✅ Cleaned"
