from rest_framework import serializers

from apps.finance.models import FinancialTransaction, LeaseAgreement, MaintenanceRecord


class LeaseAgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaseAgreement
        fields = "__all__"
        read_only_fields = ["id", "tenant", "created_at"]


class FinancialTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialTransaction
        fields = "__all__"
        read_only_fields = ["id", "tenant", "created_at"]


class MaintenanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRecord
        fields = "__all__"
        read_only_fields = ["id", "tenant", "created_at"]
