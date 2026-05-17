from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import TenantScopedModel


class TransactionType(models.TextChoices):
    LEASE_PAYMENT = "lease_payment", "Lease Payment"
    MAINTENANCE = "maintenance", "Maintenance"
    INSURANCE = "insurance", "Insurance"
    FUEL = "fuel", "Fuel"
    OTHER = "other", "Other"


class LeaseAgreement(TenantScopedModel):
    vehicle = models.OneToOneField(
        "fleet.Vehicle",
        on_delete=models.CASCADE,
        related_name="lease",
    )
    lessor_name = models.CharField(max_length=200)
    monthly_payment = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    start_date = models.DateField()
    end_date = models.DateField()
    residual_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"Lease — {self.vehicle.vin}"


class FinancialTransaction(TenantScopedModel):
    vehicle = models.ForeignKey(
        "fleet.Vehicle",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    transaction_type = models.CharField(max_length=32, choices=TransactionType.choices)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    description = models.TextField(blank=True)
    reference = models.CharField(max_length=64, blank=True)
    occurred_at = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-occurred_at", "-created_at"]

    def __str__(self):
        return f"{self.transaction_type} — {self.amount}"


class ComplianceStatus(models.TextChoices):
    COMPLIANT = "compliant", "Compliant"
    DUE_SOON = "due_soon", "Due Soon"
    OVERDUE = "overdue", "Overdue"


class MaintenanceRecord(TenantScopedModel):
    vehicle = models.ForeignKey(
        "fleet.Vehicle",
        on_delete=models.CASCADE,
        related_name="maintenance_records",
    )
    service_type = models.CharField(max_length=100)
    due_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    compliance_status = models.CharField(
        max_length=16,
        choices=ComplianceStatus.choices,
        default=ComplianceStatus.DUE_SOON,
    )
    cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_date"]

    def __str__(self):
        return f"{self.service_type} — {self.vehicle.vin}"
