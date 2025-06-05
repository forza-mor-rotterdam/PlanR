import logging

from apps.beheer.forms import (
    SpecificatieForm,
    StandaardExterneOmschrijvingAanmakenForm,
    StandaardExterneOmschrijvingAanpassenForm,
    StandaardExterneOmschrijvingSearchForm,
)
from apps.main.models import StandaardExterneOmschrijving
from apps.main.services import MORCoreService
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

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


class SpecificatieLijstView(PermissionRequiredMixin, TemplateView):
    permission_required = "authorisatie.specificatie_lijst_bekijken"
    template_name = "beheer/specificatie_lijst.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "object_list": MORCoreService()
                .specificatie_lijst(
                    params={
                        "limit": 100,
                    },
                    force_cache=True,
                    cache_timeout=3600,
                )
                .get("results", [])
            }
        )
        return context


class SpecificatieAanmakenView(PermissionRequiredMixin, FormView):
    success_url = reverse_lazy("specificatie_lijst")
    permission_required = "authorisatie.specificatie_aanmaken"
    template_name = "beheer/specificatie_form.html"
    form_class = SpecificatieForm

    def form_valid(self, form):
        form.cleaned_data.get("naam")
        response = MORCoreService().specificatie_aanmaken(
            naam=form.cleaned_data.get("naam")
        )
        print(response)
        return super().form_valid(form)


class SpecificatieAanpassenView(PermissionRequiredMixin, FormView):
    success_url = reverse_lazy("specificatie_lijst")
    permission_required = "authorisatie.specificatie_aanpassen"
    template_name = "beheer/specificatie_form.html"
    form_class = SpecificatieForm

    def get_initial(self):
        initial = self.initial.copy()
        self.object = MORCoreService().specificatie_detail(
            specificatie_uuid=self.kwargs.get("uuid"),
            force_cache=True,
            cache_timeout=3600,
        )
        initial["naam"] = self.object["naam"]
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "object": self.object,
            }
        )
        return context

    def form_valid(self, form):
        form.cleaned_data.get("naam")
        response = MORCoreService().specificatie_naam_aanpassen(
            specificatie_uuid=self.kwargs.get("uuid"),
            naam=form.cleaned_data.get("naam"),
        )
        print(response)
        return super().form_valid(form)


class SpecificatieVerwijderenView(PermissionRequiredMixin, View):
    permission_required = "authorisatie.specificatie_verwijderen"

    def get(self, request, *args, **kwargs):
        response_detail = MORCoreService().specificatie_detail(self.kwargs.get("uuid"))
        response_verwijderen = MORCoreService().specificatie_verwijderen(
            self.kwargs.get("uuid")
        )
        print(response_detail)
        print(response_verwijderen)
        messages.success(
            request, f"De specificatie '{response_detail.get('naam')}' is verwijderd"
        )
        return HttpResponse(
            f"De specificatie '{response_detail.get('naam')}' is verwijderd"
        )
