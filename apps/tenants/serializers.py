from rest_framework import serializers

from apps.tenants.models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "slug", "is_active"]
        read_only_fields = fields
