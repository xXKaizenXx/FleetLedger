from django.db import connection
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    """Liveness/readiness probe for load balancers and orchestrators."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        checks: dict[str, str] = {}
        try:
            connection.ensure_connection()
            checks["database"] = "ok"
        except Exception:
            checks["database"] = "error"

        healthy = all(v == "ok" for v in checks.values())
        return Response(
            {
                "status": "ok" if healthy else "degraded",
                "service": "fleetledger-api",
                "checks": checks,
            },
            status=200 if healthy else 503,
        )
