"""Abstract base models for tenant-scoped data."""

from django.db import models

from apps.core.managers import TenantManager


class TenantScopedModel(models.Model):
    """Every row belongs to exactly one organization (tenant)."""

    tenant = models.ForeignKey(
        "tenants.Organization",
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )

    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
