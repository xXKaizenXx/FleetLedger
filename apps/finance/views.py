from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsBranchManagerOrSuperAdmin
from apps.core.mixins import TenantWriteMixin
from apps.finance.models import FinancialTransaction, LeaseAgreement, MaintenanceRecord
from apps.finance.serializers import (
    FinancialTransactionSerializer,
    LeaseAgreementSerializer,
    MaintenanceRecordSerializer,
)
from apps.reports.tasks import generate_monthly_report_task


class LeaseAgreementViewSet(TenantWriteMixin, viewsets.ModelViewSet):
    serializer_class = LeaseAgreementSerializer

    def get_queryset(self):
        return LeaseAgreement.objects.select_related("vehicle", "tenant")


class FinancialTransactionViewSet(TenantWriteMixin, viewsets.ModelViewSet):
    serializer_class = FinancialTransactionSerializer
    filterset_fields = ["transaction_type", "occurred_at"]

    def get_queryset(self):
        return FinancialTransaction.objects.select_related("vehicle", "tenant")


class MaintenanceRecordViewSet(TenantWriteMixin, viewsets.ModelViewSet):
    serializer_class = MaintenanceRecordSerializer
    filterset_fields = ["compliance_status", "due_date"]

    def get_queryset(self):
        return MaintenanceRecord.objects.select_related("vehicle", "tenant")


class GenerateMonthlyReportView(APIView):
    """Queue end-of-month PDF generation — returns immediately with task id."""

    permission_classes = [IsBranchManagerOrSuperAdmin]

    def post(self, request):
        year = int(request.data.get("year"))
        month = int(request.data.get("month"))
        tenant_id = request.user.tenant_id
        if not tenant_id:
            return Response(
                {"detail": "Super admins must set X-Tenant-ID header."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not 1 <= month <= 12:
            return Response({"detail": "month must be 1-12."}, status=status.HTTP_400_BAD_REQUEST)

        task = generate_monthly_report_task.delay(
            tenant_id=tenant_id,
            user_id=request.user.pk,
            year=year,
            month=month,
        )
        return Response(
            {
                "detail": "Report generation queued. You will receive an encrypted PDF by email.",
                "task_id": task.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )
