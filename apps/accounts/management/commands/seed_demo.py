"""Seed two isolated tenants with sample fleet and financial data."""

from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.accounts.models import Role, User
from apps.core.context import set_bypass_tenant_filter, set_current_tenant_id
from apps.finance.models import (
    FinancialTransaction,
    LeaseAgreement,
    MaintenanceRecord,
    TransactionType,
)
from apps.fleet.models import Vehicle, VehicleStatus
from apps.tenants.models import Branch, Organization


class Command(BaseCommand):
    help = "Create demo tenants, users, vehicles, and transactions for portfolio demos."

    def handle(self, *args, **options):
        set_bypass_tenant_filter(True)

        tenants = [
            ("Barloworld Fleet SA", "barloworld-fleet"),
            ("Avis Corporate Leasing", "avis-corporate"),
        ]

        for name, slug in tenants:
            org, _ = Organization.objects.get_or_create(slug=slug, defaults={"name": name})
            branch, _ = Branch.objects.get_or_create(
                tenant=org,
                code="HQ01",
                defaults={"name": "Head Office", "city": "Johannesburg"},
            )

            manager, created = User.objects.get_or_create(
                username=f"manager@{slug}",
                defaults={
                    "email": f"manager@{slug}.local",
                    "role": Role.BRANCH_MANAGER,
                    "tenant": org,
                    "branch": branch,
                },
            )
            if created:
                manager.set_password("demo1234")
                manager.save()

            auditor, created = User.objects.get_or_create(
                username=f"auditor@{slug}",
                defaults={
                    "email": f"auditor@{slug}.local",
                    "role": Role.FLEET_AUDITOR,
                    "tenant": org,
                },
            )
            if created:
                auditor.set_password("demo1234")
                auditor.save()

            set_current_tenant_id(org.pk)
            for i in range(1, 4):
                vin = f"DEMO{slug[:4].upper()}{i:06d}X"
                vehicle, v_created = Vehicle.objects.get_or_create(
                    vin=vin,
                    defaults={
                        "tenant": org,
                        "branch": branch,
                        "make": "Toyota",
                        "model": "Hilux",
                        "year": 2023,
                        "license_plate": f"GP {100 + i}-FL",
                        "odometer_km": 15000 * i,
                        "status": VehicleStatus.ACTIVE,
                        "acquired_at": date(2023, 1, 15),
                    },
                )
                if v_created:
                    LeaseAgreement.objects.create(
                        tenant=org,
                        vehicle=vehicle,
                        lessor_name="Standard Bank Asset Finance",
                        monthly_payment=Decimal("12500.00"),
                        start_date=date(2023, 2, 1),
                        end_date=date(2028, 1, 31),
                    )
                    FinancialTransaction.objects.create(
                        tenant=org,
                        vehicle=vehicle,
                        transaction_type=TransactionType.LEASE_PAYMENT,
                        amount=Decimal("12500.00"),
                        description="Monthly lease payment",
                        reference=f"LP-{i:04d}",
                        occurred_at=date.today().replace(day=1),
                    )
                    MaintenanceRecord.objects.create(
                        tenant=org,
                        vehicle=vehicle,
                        service_type="Full service",
                        due_date=date.today().replace(month=((date.today().month % 12) + 1)),
                    )

            self.stdout.write(self.style.SUCCESS(f"Seeded tenant: {org.name}"))

        super_admin, created = User.objects.get_or_create(
            username="admin@fleetledger",
            defaults={
                "email": "admin@fleetledger.local",
                "role": Role.SUPER_ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            super_admin.set_password("demo1234")
            super_admin.save()

        self.stdout.write(self.style.SUCCESS("Demo credentials — password: demo1234"))
        self.stdout.write("  Super Admin: admin@fleetledger")
        self.stdout.write("  Managers: manager@barloworld-fleet, manager@avis-corporate")
        self.stdout.write("  Auditors: auditor@barloworld-fleet, auditor@avis-corporate")
