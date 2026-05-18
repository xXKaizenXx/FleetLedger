# FleetLedger

Multi-tenant **Finance & Compliance** engine for automotive fleet operators — Django API, React dashboard, Celery workers, OpenAPI docs, and production-ready deployment.

## Stack

| Layer | Tech |
|-------|------|
| API | Django 5.1, DRF, PostgreSQL, drf-spectacular (OpenAPI) |
| Frontend | React 19, Vite, Tailwind CSS |
| Jobs | Celery + Redis |
| Observability | Structured logging, optional Sentry |
| CI | GitHub Actions (ruff, tests, frontend build) |
| Deploy | Docker, Render Blueprint (`render.yaml`), Dependabot |

## Architecture

```
React Dashboard  →  /api/v1/*  →  TenantMiddleware  →  TenantManager
                                      ↓
                               Audit signals → AuditLog
                                      ↓
                          POST /reports/monthly/ → Celery → encrypted PDF email
```

## Quick start (local)

### Backend

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

### Frontend (separate terminal)

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** — sign in with `manager@barloworld-fleet` / `demo1234`.

### Celery + Redis

```bash
docker compose up -d redis
celery -A config worker -l info
```

## Full stack with Docker

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| Dashboard (dev) | http://localhost:5173 |
| Dashboard (production nginx) | http://localhost:8080 |
| API docs (Swagger) | http://localhost:8000/api/v1/docs/ |
| Health | http://localhost:8000/api/v1/health/ |
| Postgres | localhost:5432 |
| Redis | localhost:6379 |

Demo data is seeded when `SEED_DEMO=true` (default in Docker Compose for local demos). **Do not** set `SEED_DEMO=true` in production.

## Demo users (password: `demo1234`)

| User | Role |
|------|------|
| `admin@fleetledger` | Super Admin — pick tenant in sidebar |
| `manager@barloworld-fleet` | Branch Manager (Barloworld) |
| `auditor@avis-corporate` | Fleet Auditor (read-only, Avis) |

## Dashboard features

- Fleet vehicles, financial transactions, immutable audit trail
- Role-aware UI (auditors cannot queue reports)
- Super-admin tenant switcher (`X-Tenant-ID` header)
- One-click **Generate & email** end-of-month encrypted PDF (Celery)

## API

Base URL: `http://127.0.0.1:8000/api/v1/`

| Endpoint | Description |
|----------|-------------|
| `GET /health/` | Liveness/readiness (DB check) |
| `GET /docs/` | Swagger UI (OpenAPI) |
| `GET /schema/` | OpenAPI 3 schema (JSON) |
| `POST /auth/login/` | Session login (SPA) |
| `GET /auth/me/` | Current user |
| `GET /vehicles/` | Tenant-scoped fleet |
| `GET /audit-logs/` | Append-only audit trail |
| `POST /reports/monthly/` | Queue encrypted PDF report |

## CI

GitHub Actions runs on every push/PR:

- `python -m ruff check .`
- `python manage.py migrate` + `test` (Postgres + Redis services)
- `npm ci && npm run build` in `frontend/`

Dependabot opens weekly PRs for pip, npm, and GitHub Actions updates.

## Deploy to Render

1. Push repo to GitHub.
2. Create a **Blueprint** from `render.yaml` (API + worker + dashboard + Redis + Postgres).
3. Set environment variables after the first deploy:

| Service | Variable | Example |
|---------|----------|---------|
| API | `DJANGO_ALLOWED_HOSTS` | `fleetledger-api.onrender.com` |
| API | `CORS_ALLOWED_ORIGINS` | `https://fleetledger-dashboard.onrender.com` |
| API | `CSRF_TRUSTED_ORIGINS` | `https://fleetledger-dashboard.onrender.com` |
| Dashboard | `VITE_API_BASE_URL` | `https://fleetledger-api.onrender.com/api/v1` |
| API (optional) | `SENTRY_DSN` | Your Sentry project DSN |

4. Load demo data (see below — Render Shell is paid; use `SEED_DEMO` or local seed instead).

Migrations run automatically on each API/worker deploy via `scripts/entrypoint.sh`.

### Demo data without Render Shell (free tier)

**Option A — `SEED_DEMO` env var (easiest)**

1. Open **fleetledger-api** → **Environment** → add `SEED_DEMO` = `true`.
2. **Manual Deploy** the API (wait until live).
3. Remove `SEED_DEMO` or set it to `false` and deploy again so demo data is not re-applied on every release.

`seed_demo` is idempotent (`get_or_create`), but turning `SEED_DEMO` off after the first successful deploy is still recommended.

**Option B — seed from your machine**

1. In Render, open **fleetledger-db** → **Connections** and copy the **External Database URL**.
2. Locally:

```bash
pip install -r requirements.txt
set DATABASE_URL=postgres://...   # Windows CMD
set DJANGO_SETTINGS_MODULE=config.settings.prod
python manage.py migrate
python manage.py seed_demo
```

Use the same `DJANGO_SECRET_KEY` only if you need to match production settings; seeding only needs database access.

## Production checklist

- [ ] Strong `DJANGO_SECRET_KEY` and `REPORT_ENCRYPTION_PASSWORD` (auto-generated on Render)
- [ ] `DJANGO_DEBUG=false` and `config.settings.prod`
- [ ] HTTPS origins in `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS`
- [ ] `SEED_DEMO` unset or `false` in production
- [ ] SMTP email backend for report delivery (`EMAIL_BACKEND`, `EMAIL_HOST`, etc.)
- [ ] Optional `SENTRY_DSN` for error tracking

## Project structure

```
apps/           # Django domain apps (tenancy, fleet, finance, audit, reports)
config/         # Settings, Celery, API routes
frontend/       # React dashboard (+ Dockerfile for nginx)
scripts/        # Docker entrypoint (migrate, optional seed)
.github/        # CI workflow, Dependabot
docker-compose.yml
render.yaml
Dockerfile
SECURITY.md
```

## Portfolio talking points

1. **Defense in depth** — `TenantManager` filters every ORM query; middleware binds tenant context per request.
2. **Separation of duties** — RBAC at the API and UI layer (covered by automated tests).
3. **Compliance** — Immutable audit log with field-level diffs, actor, and IP.
4. **Production patterns** — Health probes, rate limiting, OpenAPI, encrypted deliverables, Docker entrypoint, static frontend deploy, CI, cloud blueprint.

## License

MIT — see [LICENSE](LICENSE).
