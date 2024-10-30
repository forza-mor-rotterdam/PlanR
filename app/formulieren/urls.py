from django.urls import path
from formulieren.views import BasisView

urlpatterns = [
    path("", BasisView.as_view(), name="formulieren_basis"),
]
