from django.contrib import admin

from apps.finance.models import FinancialTransaction, LeaseAgreement, MaintenanceRecord


@admin.register(LeaseAgreement)
class LeaseAgreementAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "lessor_name", "monthly_payment", "is_active", "tenant")
    list_filter = ("is_active", "tenant")


@admin.register(FinancialTransaction)
class FinancialTransactionAdmin(admin.ModelAdmin):
    list_display = ("transaction_type", "amount", "occurred_at", "tenant", "vehicle")
    list_filter = ("transaction_type", "tenant")


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "service_type", "due_date", "compliance_status", "tenant")
    list_filter = ("compliance_status", "tenant")
