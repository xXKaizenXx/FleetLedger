from django.contrib import admin

from apps.tenants.models import Branch, Organization


class BranchInline(admin.TabularInline):
    model = Branch
    extra = 0


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [BranchInline]


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "tenant", "city", "is_active")
    list_filter = ("tenant",)
