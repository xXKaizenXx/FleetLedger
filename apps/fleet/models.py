from django.db import models

from apps.core.models import TenantScopedModel


class VehicleStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    IN_MAINTENANCE = "in_maintenance", "In Maintenance"
    RETIRED = "retired", "Retired"
    LEASED_OUT = "leased_out", "Leased Out"


class Vehicle(TenantScopedModel):
    branch = models.ForeignKey(
        "tenants.Branch",
        on_delete=models.PROTECT,
        related_name="vehicles",
    )
    vin = models.CharField(max_length=17, unique=True)
    make = models.CharField(max_length=64)
    model = models.CharField(max_length=64)
    year = models.PositiveSmallIntegerField()
    license_plate = models.CharField(max_length=16, blank=True)
    odometer_km = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=VehicleStatus.choices,
        default=VehicleStatus.ACTIVE,
    )
    acquired_at = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.year} {self.make} {self.model} ({self.vin})"
