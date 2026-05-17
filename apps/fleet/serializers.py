from rest_framework import serializers

from apps.fleet.models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = [
            "id",
            "tenant",
            "branch",
            "vin",
            "make",
            "model",
            "year",
            "license_plate",
            "odometer_km",
            "status",
            "acquired_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tenant", "created_at", "updated_at"]
