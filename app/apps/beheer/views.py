import logging

from apps.beheer.forms import (
    StandaardExterneOmschrijvingAanmakenForm,
    StandaardExterneOmschrijvingAanpassenForm,
    StandaardExterneOmschrijvingSearchForm,
)
from apps.main.models import StandaardExterneOmschrijving
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, View

logger = logging.getLogger(__name__)


@login_required
@permission_required("authorisatie.beheer_bekijken", raise_exception=True)
def beheer(request):
    return render(
        request,
        "beheer/beheer.html",
        {},
    )


# Standaard tekst views
class StandaardExterneOmschrijvingView(View):
    model = StandaardExterneOmschrijving
    success_url = reverse_lazy("standaard_externe_omschrijving_lijst")


class StandaardExterneOmschrijvingLijstView(
    StandaardExterneOmschrijvingView, PermissionRequiredMixin, ListView
):
    context_object_name = "standaardteksten"
    permission_required = "authorisatie.standaard_externe_omschrijving_lijst_bekijken"
    form_class = StandaardExterneOmschrijvingSearchForm
    template_name = (
        "standaard_externe_omschrijving/standaard_externe_omschrijving_lijst.html"
    )

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search", "")
        if search:
            queryset = queryset.filter(
                Q(titel__icontains=search) | Q(tekst__icontains=search)
            )
        return queryset


class StandaardExterneOmschrijvingAanmakenView(
    SuccessMessageMixin,
    StandaardExterneOmschrijvingView,
    PermissionRequiredMixin,
    CreateView,
):
    form_class = StandaardExterneOmschrijvingAanmakenForm
    template_name = (
        "standaard_externe_omschrijving/standaard_externe_omschrijving_aanmaken.html"
    )
    permission_required = "authorisatie.standaard_externe_omschrijving_aanmaken"
    success_message = "De standaard tekst '%(titel)s' is aangemaakt"


class StandaardExterneOmschrijvingAanpassenView(
    SuccessMessageMixin,
    StandaardExterneOmschrijvingView,
    PermissionRequiredMixin,
    UpdateView,
):
    form_class = StandaardExterneOmschrijvingAanpassenForm
    template_name = (
        "standaard_externe_omschrijving/standaard_externe_omschrijving_aanpassen.html"
    )
    permission_required = "authorisatie.standaard_externe_omschrijving_aanpassen"
    success_message = "De standaard tekst '%(titel)s' is aangepast"


class StandaardExterneOmschrijvingVerwijderenView(
    StandaardExterneOmschrijvingView, PermissionRequiredMixin, DeleteView
):
    permission_required = "authorisatie.standaard_externe_omschrijving_verwijderen"
    success_message = "De standaard tekst '%(titel)s is verwijderd"

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        response = self.delete(request, *args, **kwargs)
        messages.success(request, f"De standaard tekst '{object.titel}' is verwijderd")
        return response

    # def render_to_response(self, context, **response_kwargs):
    #     return HttpResponseRedirect(self.get_success_url())
