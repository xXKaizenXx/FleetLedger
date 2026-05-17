from rest_framework import mixins, viewsets
from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.accounts.models import Role
from apps.audit.models import AuditLog
from apps.audit.serializers import AuditLogSerializer


class AuditLogReadOnlyPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.method in SAFE_METHODS and request.user.role in (
            Role.SUPER_ADMIN,
            Role.FLEET_AUDITOR,
            Role.BRANCH_MANAGER,
        )


class AuditLogViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [AuditLogReadOnlyPermission]
    filterset_fields = ["action", "model_name", "actor"]

    def get_queryset(self):
        from apps.core.context import get_bypass_tenant_filter, get_current_tenant_id

        qs = AuditLog.objects.select_related("actor", "tenant")
        if get_bypass_tenant_filter():
            return qs
        tenant_id = get_current_tenant_id()
        if tenant_id:
            return qs.filter(tenant_id=tenant_id)
        return qs.none()
