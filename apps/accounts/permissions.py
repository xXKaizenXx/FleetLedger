"""Role-based access control for the REST API."""

from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.accounts.models import Role


class TenantRBACPermission(BasePermission):
    """
    Super Admin: full access (optionally scoped via X-Tenant-ID header).
    Branch Manager: read/write within their tenant (and branch when set).
    Fleet Auditor: read-only on financial and fleet data.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.role == Role.SUPER_ADMIN:
            return True

        if user.role == Role.FLEET_AUDITOR:
            return request.method in SAFE_METHODS

        if user.role == Role.BRANCH_MANAGER:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == Role.SUPER_ADMIN:
            return True

        tenant_id = getattr(obj, "tenant_id", None)
        if tenant_id and user.tenant_id and tenant_id != user.tenant_id:
            return False

        if user.role == Role.FLEET_AUDITOR:
            return request.method in SAFE_METHODS

        if user.role == Role.BRANCH_MANAGER and user.branch_id:
            branch_id = getattr(obj, "branch_id", None)
            if branch_id is not None:
                return branch_id == user.branch_id

        return user.role == Role.BRANCH_MANAGER


class IsBranchManagerOrSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in (Role.SUPER_ADMIN, Role.BRANCH_MANAGER)
