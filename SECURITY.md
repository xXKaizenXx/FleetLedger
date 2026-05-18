# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| main    | Yes       |

## Reporting a Vulnerability

If you discover a security issue, please **do not** open a public GitHub issue.

Email a private report with:

- Description of the vulnerability and impact
- Steps to reproduce
- Affected components (API, dashboard, Celery worker, etc.)

We aim to acknowledge reports within 5 business days.

## Security Practices (FleetLedger)

- **Multi-tenancy**: ORM queries are scoped via `TenantManager`; tenant context is set per request in middleware.
- **RBAC**: API default permission class enforces role-based access; auditors are read-only.
- **Audit trail**: Field-level changes are logged with actor and IP.
- **Production**: Use `config.settings.prod`, strong `DJANGO_SECRET_KEY`, HTTPS, and restrict `CORS_ALLOWED_ORIGINS` / `CSRF_TRUSTED_ORIGINS`.
- **Reports**: PDFs are encrypted at rest in transit to recipients; set `REPORT_ENCRYPTION_PASSWORD` via a secrets manager in production.
