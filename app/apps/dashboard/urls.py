from apps.dashboard.views import DashboardV2
from django.urls import path

urlpatterns = [
    # Dashboard
    path(
        "",
        DashboardV2.as_view(),
        name="dashboard",
    ),
]
