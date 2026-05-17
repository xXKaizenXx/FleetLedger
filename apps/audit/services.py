"""Audit logging service — the only code path that writes AuditLog rows."""

from __future__ import annotations

from typing import Any

from django.forms.models import model_to_dict

from apps.audit.models import AuditAction, AuditLog


def _serialize(value: Any) -> Any:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, (str, int, float, bool, type(None))):
        return value
    return str(value)


def snapshot_instance(instance) -> dict:
    data = model_to_dict(instance)
    return {k: _serialize(v) for k, v in data.items()}


def diff_snapshots(before: dict, after: dict) -> dict:
    changes = {}
    for key in set(before) | set(after):
        if before.get(key) != after.get(key):
            changes[key] = {"old": before.get(key), "new": after.get(key)}
    return changes


def write_audit_log(
    *,
    tenant_id: int,
    actor_id: int | None,
    action: str,
    instance,
    changes: dict | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    return AuditLog.objects.create(
        tenant_id=tenant_id,
        actor_id=actor_id,
        action=action,
        model_name=instance._meta.label_lower,
        object_id=str(instance.pk),
        object_repr=str(instance)[:255],
        changes=changes or {},
        ip_address=ip_address,
    )


def log_create(instance, *, actor_id=None, ip_address=None):
    return write_audit_log(
        tenant_id=instance.tenant_id,
        actor_id=actor_id,
        action=AuditAction.CREATE,
        instance=instance,
        changes={"after": snapshot_instance(instance)},
        ip_address=ip_address,
    )


def log_update(instance, *, before: dict, actor_id=None, ip_address=None):
    after = snapshot_instance(instance)
    return write_audit_log(
        tenant_id=instance.tenant_id,
        actor_id=actor_id,
        action=AuditAction.UPDATE,
        instance=instance,
        changes=diff_snapshots(before, after),
        ip_address=ip_address,
    )


def log_delete(instance, *, before: dict, actor_id=None, ip_address=None):
    return write_audit_log(
        tenant_id=instance.tenant_id,
        actor_id=actor_id,
        action=AuditAction.DELETE,
        instance=instance,
        changes={"before": before},
        ip_address=ip_address,
    )
