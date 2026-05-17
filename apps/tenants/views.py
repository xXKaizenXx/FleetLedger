from rest_framework import viewsets
from rest_framework.permissions import BasePermission

from apps.accounts.models import Role
from apps.tenants.models import Organization
from apps.tenants.serializers import OrganizationSerializer


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == Role.SUPER_ADMIN


class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    """Super admins can list tenants to scope the dashboard via X-Tenant-ID."""

    queryset = Organization.objects.filter(is_active=True)
    serializer_class = OrganizationSerializer
    permission_classes = [IsSuperAdmin]
