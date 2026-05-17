from rest_framework import serializers

from apps.accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    tenant_name = serializers.CharField(source="tenant.name", read_only=True, allow_null=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "role_display",
            "tenant",
            "tenant_name",
            "branch",
            "branch_name",
        ]
        read_only_fields = fields
