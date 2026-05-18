from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Role, User
from apps.fleet.models import Vehicle
from apps.tenants.models import Branch, Organization


class RBACAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.org = Organization.objects.create(name="RBAC Fleet", slug="rbac-fleet")
        self.branch = Branch.objects.create(tenant=self.org, name="HQ", code="RB1")

        self.manager = User.objects.create_user(
            username="manager@rbac-fleet",
            password="demo1234",
            role=Role.BRANCH_MANAGER,
            tenant=self.org,
            branch=self.branch,
        )
        self.auditor = User.objects.create_user(
            username="auditor@rbac-fleet",
            password="demo1234",
            role=Role.FLEET_AUDITOR,
            tenant=self.org,
        )

        Vehicle.all_objects.create(
            tenant=self.org,
            branch=self.branch,
            vin="1HGBH41JXMN109186",
            make="Ford",
            model="Ranger",
            year=2024,
            acquired_at="2024-01-01",
        )

    def test_auditor_can_list_vehicles(self):
        self.assertEqual(Vehicle.all_objects.filter(tenant=self.org).count(), 1)
        self.client.force_login(self.auditor)
        response = self.client.get("/api/v1/vehicles/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

    def test_auditor_cannot_create_vehicle(self):
        self.client.force_login(self.auditor)
        response = self.client.post(
            "/api/v1/vehicles/",
            {
                "vin": "NEWVIN12345678901",
                "make": "Toyota",
                "model": "Hilux",
                "year": 2024,
                "branch": self.branch.pk,
                "acquired_at": "2024-06-01",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_manager_can_create_vehicle(self):
        self.client.force_login(self.manager)
        response = self.client.post(
            "/api/v1/vehicles/",
            {
                "vin": "NEWVIN12345678902",
                "make": "Toyota",
                "model": "Hilux",
                "year": 2024,
                "branch": self.branch.pk,
                "acquired_at": "2024-06-01",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
