"""Ensure demo vehicles exist (Render entrypoint seed can miss fleet rows)."""

from datetime import date

from django.db import migrations


def seed_demo_vehicles(apps, schema_editor):
    Vehicle = apps.get_model("fleet", "Vehicle")
    Organization = apps.get_model("tenants", "Organization")
    Branch = apps.get_model("tenants", "Branch")

    if Vehicle.objects.exists():
        return

    tenants = [
        ("barloworld-fleet", "DEMOBARL"),
        ("avis-corporate", "DEMOAVIS"),
    ]
    for slug, vin_prefix in tenants:
        org = Organization.objects.filter(slug=slug).first()
        if not org:
            continue
        branch = Branch.objects.filter(tenant_id=org.id, code="HQ01").first()
        if not branch:
            continue
        for i in range(1, 4):
            Vehicle.objects.create(
                tenant_id=org.id,
                branch_id=branch.id,
                vin=f"{vin_prefix}{i:06d}X",
                make="Toyota",
                model="Hilux",
                year=2023,
                license_plate=f"GP {100 + i}-FL",
                odometer_km=15000 * i,
                status="active",
                acquired_at=date(2023, 1, 15),
            )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("fleet", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_demo_vehicles, noop),
    ]
