from rest_framework import viewsets

from apps.core.mixins import TenantWriteMixin
from apps.fleet.models import Vehicle
from apps.fleet.serializers import VehicleSerializer


class VehicleViewSet(TenantWriteMixin, viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    filterset_fields = ["status", "branch", "make"]
    search_fields = ["vin", "make", "model", "license_plate"]

    def get_queryset(self):
        return Vehicle.objects.select_related("branch", "tenant")
