"""QuerySet/Manager that enforces tenant isolation at the ORM layer."""

from __future__ import annotations

from django.db import models

from apps.core.context import get_bypass_tenant_filter, get_current_tenant_id


class TenantQuerySet(models.QuerySet):
    def for_tenant(self, tenant_id: int):
        return self.filter(tenant_id=tenant_id)


class TenantManager(models.Manager):
    """Automatically scopes all queries to the active tenant."""

    def get_queryset(self):
        qs = TenantQuerySet(self.model, using=self._db)
        if get_bypass_tenant_filter():
            return qs
        tenant_id = get_current_tenant_id()
        if tenant_id is None:
            return qs.none()
        return qs.filter(tenant_id=tenant_id)

    def unscoped(self):
        return TenantQuerySet(self.model, using=self._db)
