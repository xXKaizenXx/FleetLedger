"""DRF mixins that bind audit context and enforce tenant on writes."""

from apps.core.context import get_current_tenant_id, set_audit_context


class TenantWriteMixin:
    """Assign tenant from middleware context on create."""

    def perform_create(self, serializer):
        tenant_id = get_current_tenant_id()
        if tenant_id is None and hasattr(self.request.user, "tenant_id"):
            tenant_id = self.request.user.tenant_id
        serializer.save(tenant_id=tenant_id)

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        ip = request.META.get("REMOTE_ADDR")
        actor_id = request.user.pk if request.user.is_authenticated else None
        set_audit_context(actor_id=actor_id, ip_address=ip)
