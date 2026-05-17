"""Thread-local tenant context — set by TenantMiddleware per request."""

from __future__ import annotations

import threading

_local = threading.local()


def get_current_tenant_id() -> int | None:
    return getattr(_local, "tenant_id", None)


def set_current_tenant_id(tenant_id: int | None) -> None:
    _local.tenant_id = tenant_id


def get_bypass_tenant_filter() -> bool:
    return getattr(_local, "bypass_tenant_filter", False)


def set_bypass_tenant_filter(bypass: bool) -> None:
    _local.bypass_tenant_filter = bypass


def clear_tenant_context() -> None:
    _local.tenant_id = None
    _local.bypass_tenant_filter = False
    _local.audit_actor_id = None
    _local.audit_ip = None


def set_audit_context(*, actor_id: int | None = None, ip_address: str | None = None) -> None:
    _local.audit_actor_id = actor_id
    _local.audit_ip = ip_address


def get_audit_actor_id() -> int | None:
    return getattr(_local, "audit_actor_id", None)


def get_audit_ip() -> str | None:
    return getattr(_local, "audit_ip", None)
