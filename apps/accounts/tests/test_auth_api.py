from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Role, User
from apps.tenants.models import Branch, Organization


class AuthAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.org = Organization.objects.create(name="Test Fleet", slug="test-fleet")
        self.branch = Branch.objects.create(tenant=self.org, name="HQ", code="HQ1")
        self.user = User.objects.create_user(
            username="manager@test-fleet",
            password="secure-pass-1",
            role=Role.BRANCH_MANAGER,
            tenant=self.org,
            branch=self.branch,
        )

    def test_health_endpoint_is_public(self):
        response = self.client.get("/api/v1/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(response.json()["checks"]["database"], "ok")

    def test_login_success(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": "manager@test-fleet", "password": "secure-pass-1"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "manager@test-fleet")

    def test_login_invalid_credentials(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": "manager@test-fleet", "password": "wrong"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_me_requires_authentication(self):
        response = self.client.get("/api/v1/auth/me/")
        self.assertEqual(response.status_code, 403)

    def test_me_returns_current_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/auth/me/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["role"], Role.BRANCH_MANAGER)
