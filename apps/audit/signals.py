"""Automatic immutable audit trail for financial and fleet models."""

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from apps.audit.services import log_create, log_delete, log_update, snapshot_instance
from apps.core.context import get_audit_actor_id, get_audit_ip
from apps.finance.models import FinancialTransaction, LeaseAgreement, MaintenanceRecord
from apps.fleet.models import Vehicle

AUDITED_MODELS = (Vehicle, LeaseAgreement, FinancialTransaction, MaintenanceRecord)
_pre_save_cache: dict = {}


def _cache_key(sender, pk):
    return f"{sender._meta.label}:{pk}"


@receiver(pre_save)
def capture_pre_save_state(sender, instance, **kwargs):
    if sender not in AUDITED_MODELS or not instance.pk:
        return
    try:
        old = sender.all_objects.get(pk=instance.pk)
        _pre_save_cache[_cache_key(sender, instance.pk)] = snapshot_instance(old)
    except sender.DoesNotExist:
        pass


@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    if sender not in AUDITED_MODELS:
        return
    actor_id = get_audit_actor_id()
    ip = get_audit_ip()
    if created:
        log_create(instance, actor_id=actor_id, ip_address=ip)
        return
    key = _cache_key(sender, instance.pk)
    before = _pre_save_cache.pop(key, {})
    if before:
        log_update(instance, before=before, actor_id=actor_id, ip_address=ip)


@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    if sender not in AUDITED_MODELS:
        return
    log_delete(
        instance,
        before=snapshot_instance(instance),
        actor_id=get_audit_actor_id(),
        ip_address=get_audit_ip(),
    )
