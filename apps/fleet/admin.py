from django.contrib import admin

from apps.fleet.models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("vin", "make", "model", "year", "status", "tenant", "branch")
    list_filter = ("status", "tenant", "branch")
    search_fields = ("vin", "make", "model")
