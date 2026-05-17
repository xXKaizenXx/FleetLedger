# FleetLedger

Multi-tenant **Finance & Compliance** engine for automotive fleet operators — Django API, React dashboard, Celery workers, and CI/CD.

## Stack

| Layer | Tech |
|-------|------|
| API | Django 5.1, DRF, PostgreSQL |
| Frontend | React 19, Vite, Tailwind CSS |
| Jobs | Celery + Redis |
| CI | GitHub Actions (ruff, tests, frontend build) |
| Deploy | Docker, Render Blueprint (`render.yaml`) |

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
| Dashboard | http://localhost:5173 |
| Postgres | localhost:5432 |
| Redis | localhost:6379 |

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

## Deploy to Render

1. Push repo to GitHub.
2. Create a **Blueprint** from `render.yaml` (web + worker + Redis + Postgres).
3. Set `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` to your frontend URL.

## Project structure

```
apps/           # Django domain apps (tenancy, fleet, finance, audit, reports)
config/         # Settings, Celery, API routes
frontend/       # React dashboard
.github/        # CI workflow
docker-compose.yml
render.yaml
Dockerfile
```

## Portfolio talking points

1. **Defense in depth** — `TenantManager` filters every ORM query; middleware binds tenant context per request.
2. **Separation of duties** — RBAC at the API and UI layer.
3. **Compliance** — Immutable audit log with field-level diffs, actor, and IP.
4. **Production patterns** — Async reporting, encrypted deliverables, Docker, CI, cloud blueprint.

## License

MIT — portfolio use.
