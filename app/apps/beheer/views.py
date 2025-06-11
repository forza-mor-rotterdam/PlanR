import logging

from apps.beheer.forms import (
    MeldingAfhandelredenForm,
    SpecificatieForm,
    StandaardExterneOmschrijvingForm,
    StandaardExterneOmschrijvingSearchForm,
)
from apps.main.models import (
    SPECIFICATIE_CACHE_TIMEOUT,
    STATUS_NIET_OPGELOST_REDENEN_CHOICES,
    STATUS_NIET_OPGELOST_REDENEN_TITEL,
    ZICHTBAARHEID_TITEL,
    MeldingAfhandelreden,
    StandaardExterneOmschrijving,
)
from apps.main.services import MORCoreService
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "STATUS_NIET_OPGELOST_REDENEN_TITEL": STATUS_NIET_OPGELOST_REDENEN_TITEL,
                "ZICHTBAARHEID_TITEL": ZICHTBAARHEID_TITEL,
            }
        )
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by("titel")


class StandaardExterneOmschrijvingMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(list(MeldingAfhandelreden.objects.values("reden", "specificatie_opties")))
        context.update(
            {
                "melding_afhandelreden_lijst": list(
                    MeldingAfhandelreden.objects.values("id", "specificatie_opties")
                ),
            }
        )
        return context


class StandaardExterneOmschrijvingAanmakenView(
    StandaardExterneOmschrijvingMixin,
    SuccessMessageMixin,
    StandaardExterneOmschrijvingView,
    PermissionRequiredMixin,
    CreateView,
):
    form_class = StandaardExterneOmschrijvingForm
    template_name = (
        "standaard_externe_omschrijving/standaard_externe_omschrijving_form.html"
    )
    permission_required = "authorisatie.standaard_externe_omschrijving_aanmaken"
    success_message = "De standaard tekst '%(titel)s' is aangemaakt"


class StandaardExterneOmschrijvingAanpassenView(
    StandaardExterneOmschrijvingMixin,
    SuccessMessageMixin,
    StandaardExterneOmschrijvingView,
    PermissionRequiredMixin,
    UpdateView,
):
    form_class = StandaardExterneOmschrijvingForm
    template_name = (
        "standaard_externe_omschrijving/standaard_externe_omschrijving_form.html"
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


class MeldingAfhandelredenLijstView(
    PermissionRequiredMixin,
    ListView,
):
    queryset = MeldingAfhandelreden.objects.order_by("reden")
    permission_required = "authorisatie.melding_afhandelreden_lijst_bekijken"
    template_name = "beheer/melding_afhandelreden_lijst.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "STATUS_NIET_OPGELOST_REDENEN_TITEL": STATUS_NIET_OPGELOST_REDENEN_TITEL,
                "STATUS_NIET_OPGELOST_REDENEN_CHOICES": STATUS_NIET_OPGELOST_REDENEN_CHOICES,
            }
        )
        return context


class MeldingAfhandelredenMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        standaard_externe_omschrijving_lijst = [
            standaard_externe_omschrijving
            | {
                "aanpassen_url": reverse(
                    "standaard_externe_omschrijving_aanpassen",
                    args=[standaard_externe_omschrijving["id"]],
                )
            }
            for standaard_externe_omschrijving in list(
                self.object.standaard_externe_omschrijvingen_voor_melding_afhandelreden.values(
                    "id", "specificatie_opties", "titel"
                )
                if self.object
                else []
            )
        ]
        context.update(
            {
                "STATUS_NIET_OPGELOST_REDENEN_TITEL": STATUS_NIET_OPGELOST_REDENEN_TITEL,
                "standaard_externe_omschrijving_lijst": standaard_externe_omschrijving_lijst,
            }
        )
        return context


class MeldingAfhandelredenAanmakenView(
    MeldingAfhandelredenMixin,
    SuccessMessageMixin,
    PermissionRequiredMixin,
    CreateView,
):
    queryset = MeldingAfhandelreden.objects.all()
    success_url = reverse_lazy("melding_afhandelreden_lijst")
    permission_required = "authorisatie.melding_afhandelreden_aanmaken"
    template_name = "beheer/melding_afhandelreden_form.html"
    form_class = MeldingAfhandelredenForm
    success_message = "De melding afhandelreden '%(reden)s is aangemaakt"

    def get_success_url(self):
        return reverse_lazy("melding_afhandelreden_aanpassen", args=[self.object.id])


class MeldingAfhandelredenAanpassenView(
    MeldingAfhandelredenMixin,
    SuccessMessageMixin,
    PermissionRequiredMixin,
    UpdateView,
):
    queryset = MeldingAfhandelreden.objects.all()
    success_url = reverse_lazy("melding_afhandelreden_lijst")
    permission_required = "authorisatie.melding_afhandelreden_aanpassen"
    template_name = "beheer/melding_afhandelreden_form.html"
    form_class = MeldingAfhandelredenForm
    success_message = "De melding afhandelreden '%(reden)s is aangepast"

    def get_success_url(self):
        reden = self.object
        standaard_externe_omschrijving_lijst = [
            standaard_externe_omschrijving
            for standaard_externe_omschrijving in reden.standaard_externe_omschrijvingen_voor_melding_afhandelreden.filter(
                specificatie_opties__isnull=False,
            ).exclude(
                specificatie_opties__contained_by=reden.specificatie_opties
            )
        ]
        for standaard_externe_omschrijving in standaard_externe_omschrijving_lijst:
            standaard_externe_omschrijving.specificatie_opties = []
        StandaardExterneOmschrijving.objects.bulk_update(
            standaard_externe_omschrijving_lijst, ["specificatie_opties"]
        )
        return reverse_lazy("melding_afhandelreden_aanpassen", args=[reden.id])


class MeldingAfhandelredenVerwijderenView(PermissionRequiredMixin, DeleteView):
    queryset = MeldingAfhandelreden.objects.all()
    permission_required = "authorisatie.melding_afhandelreden_verwijderen"
    success_url = reverse_lazy("melding_afhandelreden_lijst")

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        response = self.delete(request, *args, **kwargs)
        messages.success(
            request, f"De melding afhandelreden '{object.reden}' is verwijderd"
        )
        return response


class SpecificatieLijstView(PermissionRequiredMixin, TemplateView):
    permission_required = "authorisatie.specificatie_lijst_bekijken"
    template_name = "beheer/specificatie_lijst.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        def get_melding_afhandelreden(specificatie_url):
            reden = MeldingAfhandelreden.objects.filter(
                specificatie_opties__isnull=False,
                specificatie_opties__contains=[specificatie_url],
            ).first()
            if reden:
                return {
                    "reden": reden.reden,
                    "aanpassen_url": reverse_lazy(
                        "melding_afhandelreden_aanpassen", args=[reden.id]
                    ),
                }
            return {}

        specificatie_lijst = (
            MORCoreService()
            .specificatie_lijst(
                params={
                    "limit": 100,
                },
                force_cache=True,
                cache_timeout=SPECIFICATIE_CACHE_TIMEOUT,
            )
            .get("results", [])
        )
        gebruikte_specificatie_urls = list(
            set(
                [
                    url
                    for url_list in StandaardExterneOmschrijving.objects.filter(
                        specificatie_opties__isnull=False
                    ).values_list("specificatie_opties", flat=True)
                    for url in url_list
                ]
            )
        )

        specificatie_lijst = [
            specificatie
            | {
                "reden": get_melding_afhandelreden(
                    specificatie.get("_links", {}).get("self")
                )
            }
            for specificatie in specificatie_lijst
        ]
        print("gebruikte_specificatie_urls")
        print(gebruikte_specificatie_urls)
        context.update(
            {
                "object_list": specificatie_lijst,
                "gebruikte_specificatie_urls": gebruikte_specificatie_urls,
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
