from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "role", "tenant", "branch", "is_active")
    list_filter = ("role", "tenant", "is_active")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("FleetLedger", {"fields": ("role", "tenant", "branch")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("FleetLedger", {"fields": ("role", "tenant", "branch")}),
    )
