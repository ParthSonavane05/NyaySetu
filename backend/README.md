# NyaySetu Backend

Multi-tenant SaaS backend for Indian revenue-law firms.

## Stack

Python 3.12 · FastAPI · Pydantic v2 · SQLAlchemy 2.0 (async) · PostgreSQL 16 (pgvector, pg_trgm, citext, pgcrypto) · Redis · Celery · S3/MinIO · Docker

## Quick Start

### 1. Docker Compose (recommended)

```bash
cd backend
cp .env.example .env
docker compose up -d --build
```

API available at **http://localhost:8000** · Docs at **http://localhost:8000/docs**

### 2. Local Development

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

pip install -e ".[dev]"
pre-commit install
cp .env.example .env          # edit as needed

# Start Postgres, Redis, MinIO (if not using docker compose)
uvicorn app.main:app --reload
```

## Running Tests

```bash
# Requires DATABASE_URL, REDIS_URL, SECRET_KEY, S3_ACCESS_KEY, S3_SECRET_KEY env vars
# (set in .env or export them)

pytest tests/ -v --tb=short

# With coverage
pytest tests/ -v --tb=short --cov=app --cov-report=term-missing
```

**Offline tests** (pagination, text normalisation, error format) run without any external services.

## Health Checks

| Endpoint         | Purpose                        |
| ---------------- | ------------------------------ |
| `GET /health/live`  | Liveness – always 200       |
| `GET /health/ready` | Readiness – checks DB, Redis, S3 |

## Project Layout

```
backend/
├── app/
│   ├── core/           # Config, DB, errors, logging, pagination, rate-limit, security, tenancy
│   ├── modules/
│   │   └── health/     # Health-check endpoints
│   └── workers/        # Celery app
├── alembic/            # Database migrations
├── tests/              # Test suite
├── scripts/            # DB init scripts
├── Dockerfile          # Multi-stage, non-root
├── docker-compose.yml  # api + postgres + redis + minio
├── Makefile            # Dev shortcuts
└── pyproject.toml      # Dependencies & tool config
```

## Key Design Decisions

- **Modular monolith**: modules communicate through service interfaces only
- **Multi-tenancy**: every tenant table uses `firm_id` + PostgreSQL RLS; `SET LOCAL app.firm_id` set per-request
- **404 not 403**: `PermissionDeniedError` maps to 404 to avoid leaking resource existence
- **RFC 7807 errors**: every error response includes `code`, `detail`, `request_id`
- **UUIDv7 IDs**: time-sortable, via `uuid-utils`
- **Structured logging**: `structlog` JSON output; no request bodies logged
- **Security headers**: nosniff, DENY frames, strict referrer policy

## Make Targets

```
make help       # Show all targets
make dev        # Install dev deps + pre-commit
make up         # docker compose up
make down       # docker compose down
make test       # Run tests
make lint       # ruff + mypy
make format     # Auto-format
make migrate    # Run Alembic migrations
```

