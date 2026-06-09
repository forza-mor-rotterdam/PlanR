from django.http import HttpResponse
from health_check.views import MainView
from rest_framework import status


def healthz(request):
    return HttpResponse("ok")


class HealthCheckView(MainView):
    def get(self, request, *args, **kwargs):
        # Geef 503 terug in plaats van 500 als een health-check faalt
        response = super().get(request, *args, **kwargs)
        if response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return response
