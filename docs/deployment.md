# Deployment Guide

The BehaveDrift API is built on modern, lightweight, async-first Python standards. Deploying the system into production requires orchestrating its relational store (PostgreSQL) alongside the API service logic and robust memory caches for API traffic coordination.

## Production Prerequisites

1. **Database:** PostgreSQL `>= 14` equipped running `asyncpg` bindings.
2. **Key-Value Cache:** Redis `>= 6` configuration for rate limiting state storage.
3. **Container Infrastructure:** Docker with Kubernetes, or standard Docker Compose configuration.
4. **Environment Secrets Manager:** e.g., AWS Secrets Manager, GitHub Secrets holding standard `.env` variables.

---

## 1. Environment Configurations
Prepare an environment file defining your production setup.
Do **not** use the default development configurations in production.

```ini
APP_ENV=production
DEBUG=False
LOG_LEVEL=INFO
LOG_FORMAT=json

# Update these URLs with production-ready hosts with strict passwords
DATABASE_URL=postgresql+asyncpg://behavedrift_prod:secure_password@db_host:5432/behavedrift_prod
REDIS_URL=redis://redis_host:6379/0

# Enforce RS256 algorithm securely
JWT_ALGORITHM=RS256

# Restrict hosts
ALLOWED_HOSTS=["https://api.yourorganization.com"]
```

---

## 2. Running migrations 

The API leverages `Alembic` to safely migrate database clusters. Before exposing the platform, ensure the schema generation is triggered manually. 

```bash
alembic upgrade head
```

> [!WARNING]
> Ensure the connection URL supplied exactly matches the SQL constraints required by constraints such as `ondelete="CASCADE"`. Schema updates must be run directly on an isolated task environment connected to the primary data tier, prior to blue/green API swaps.

---

## 3. Container Depoloyment

We heavily recommend building the system into Docker artifacts natively. The included `Dockerfile` correctly maps the port to `$PORT`.

```bash
docker pull ghcr.io/ummaruje/behavedrift-api:latest

docker run -d \
  -p 8000:8000 \
  --name behavedrift-api-prod \
  --env-file .env \
  --restart always \
  ghcr.io/ummaruje/behavedrift-api:latest
```

### High Availability Note
FastAPI operations are entirely stateless. You may securely scale out to several parallel instances using tools such as Kubernetes Replicasets. Global limits—like token regeneration caps—fall back intelligently to your core Redis configuration automatically.
