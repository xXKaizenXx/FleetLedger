from apps.accounts.views import CsrfView, LoginView, LogoutView, MeView
from apps.audit.views import AuditLogViewSet
from apps.finance.views import (
    FinancialTransactionViewSet,
    GenerateMonthlyReportView,
    LeaseAgreementViewSet,
    MaintenanceRecordViewSet,
)
from apps.fleet.views import VehicleViewSet
from apps.tenants.views import OrganizationViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"organizations", OrganizationViewSet, basename="organization")
router.register(r"vehicles", VehicleViewSet, basename="vehicle")
router.register(r"leases", LeaseAgreementViewSet, basename="lease")
router.register(r"transactions", FinancialTransactionViewSet, basename="transaction")
router.register(r"maintenance", MaintenanceRecordViewSet, basename="maintenance")
router.register(r"audit-logs", AuditLogViewSet, basename="audit-log")

urlpatterns = [
    path("auth/csrf/", CsrfView.as_view(), name="auth-csrf"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
    path("", include(router.urls)),
    path("reports/monthly/", GenerateMonthlyReportView.as_view(), name="monthly-report"),
]
