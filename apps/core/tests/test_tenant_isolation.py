from django.test import TestCase

from apps.core.context import clear_tenant_context, set_current_tenant_id
from apps.fleet.models import Vehicle
from apps.tenants.models import Branch, Organization


class TenantIsolationTests(TestCase):
    def setUp(self):
        self.org_a = Organization.objects.create(name="Tenant A", slug="tenant-a")
        self.org_b = Organization.objects.create(name="Tenant B", slug="tenant-b")
        self.branch_a = Branch.objects.create(tenant=self.org_a, name="A HQ", code="A1")
        self.branch_b = Branch.objects.create(tenant=self.org_b, name="B HQ", code="B1")

        Vehicle.all_objects.create(
            tenant=self.org_a,
            branch=self.branch_a,
            vin="1HGBH41JXMN109186",
            make="Ford",
            model="Ranger",
            year=2024,
            acquired_at="2024-01-01",
        )
        Vehicle.all_objects.create(
            tenant=self.org_b,
            branch=self.branch_b,
            vin="2HGFG3B54CH501234",
            make="Toyota",
            model="Corolla",
            year=2024,
            acquired_at="2024-01-01",
        )

    def tearDown(self):
        clear_tenant_context()

    def test_tenant_manager_filters_queries(self):
        set_current_tenant_id(self.org_a.pk)
        vehicles = list(Vehicle.objects.values_list("vin", flat=True))
        self.assertEqual(vehicles, ["1HGBH41JXMN109186"])

        set_current_tenant_id(self.org_b.pk)
        vehicles = list(Vehicle.objects.values_list("vin", flat=True))
        self.assertEqual(vehicles, ["2HGFG3B54CH501234"])

    def test_no_tenant_context_returns_empty_queryset(self):
        clear_tenant_context()
        self.assertEqual(Vehicle.objects.count(), 0)
