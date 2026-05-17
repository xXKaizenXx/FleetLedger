"""
Tenant isolation middleware.

On each authenticated request, binds the user's organization to thread-local
context so TenantManager filters every ORM query automatically.
"""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse

from apps.accounts.models import Role
from apps.core.context import (
    clear_tenant_context,
    set_bypass_tenant_filter,
    set_current_tenant_id,
)


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        clear_tenant_context()
        self._bind_tenant(request)
        try:
            return self.get_response(request)
        finally:
            clear_tenant_context()

    def _bind_tenant(self, request: HttpRequest) -> None:
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return

        if user.role == Role.SUPER_ADMIN:
            header = request.META.get("HTTP_X_TENANT_ID")
            if header:
                set_current_tenant_id(int(header))
            else:
                set_bypass_tenant_filter(True)
            return

        if user.tenant_id:
            set_current_tenant_id(user.tenant_id)
