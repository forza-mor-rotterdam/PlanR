import logging
import math

from apps.beheer.forms import (
    MeldingAfhandelredenForm,
    SpecificatieForm,
    StandaardExterneOmschrijvingForm,
    StandaardExterneOmschrijvingSearchForm,
    TaakopdrachtTaakAanmakenIssueLijstForm,
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
from django.shortcuts import redirect, render
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
                    "id", "specificatie_opties", "titel", "reden"
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
    success_message = "De melding afhandelreden '%(reden_verbose)s' is aangemaakt"

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            reden_verbose=self.object.reden_verbose,
        )

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
    success_message = "De melding afhandelreden '%(reden_verbose)s' is aangepast"

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            reden_verbose=self.object.reden_verbose,
        )

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
            request, f"De melding afhandelreden '{object.reden_verbose}' is verwijderd"
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

        specificatie_lijst = MORCoreService().specificatie_lijst(
            params={
                "limit": 100,
                "is_verwijderd": False,
            },
            force_cache=True,
            cache_timeout=SPECIFICATIE_CACHE_TIMEOUT,
        )
        if specificatie_lijst.get("error"):
            messages.error(
                self.request, "Er ging iets mis met het ophalen van de specificaties"
            )
        specificatie_lijst = specificatie_lijst.get("results", [])

        verwijderde_specificatie_lijst = (
            MORCoreService()
            .specificatie_lijst(
                params={
                    "limit": 100,
                    "is_verwijderd": True,
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

        specificatie_lijst = sorted(
            [
                specificatie
                | {
                    "reden": get_melding_afhandelreden(
                        specificatie.get("_links", {}).get("self", {}).get("href")
                    )
                }
                for specificatie in specificatie_lijst
            ],
            key=lambda o: o.get("naam"),
        )
        context.update(
            {
                "object_list": specificatie_lijst,
                "verwijderde_specificatie_lijst": verwijderde_specificatie_lijst,
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
        response = MORCoreService().specificatie_aanmaken(
            naam=form.cleaned_data.get("naam")
        )
        if response.get("error"):
            messages.error(
                self.request,
                f"Er ging iets mis met het aanmaken van de specificatie '{form.cleaned_data.get('naam')}'",
            )
        else:
            messages.success(
                self.request,
                f"De specificatie '{form.cleaned_data.get('naam')}' is aangemaakt",
            )

        return super().form_valid(form)


class SpecificatieAanpassenView(PermissionRequiredMixin, FormView):
    success_url = reverse_lazy("specificatie_lijst")
    permission_required = "authorisatie.specificatie_aanpassen"
    template_name = "beheer/specificatie_form.html"
    form_class = SpecificatieForm

    def dispatch(self, request, *args, **kwargs):
        response = MORCoreService().specificatie_detail(
            specificatie_uuid=self.kwargs.get("uuid"),
            force_cache=True,
            cache_timeout=3600,
        )
        self.object = None
        if response.get("error"):
            messages.error(
                self.request, "Er ging iets mis met het ophalen van de specificatie"
            )
            return redirect(reverse("specificatie_lijst"))
        self.object = response
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = self.initial.copy()
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
        if response.get("error"):
            messages.error(
                self.request,
                f"Er ging iets mis met het aanpassen van de specificatie '{form.cleaned_data.get('naam')}'",
            )
        else:
            messages.success(
                self.request,
                f"De specificatie '{form.cleaned_data.get('naam')}' is aangepast",
            )

        return super().form_valid(form)


class SpecificatieVerwijderenView(PermissionRequiredMixin, View):
    permission_required = "authorisatie.specificatie_verwijderen"

    def get(self, request, *args, **kwargs):
        response_detail = MORCoreService().specificatie_detail(self.kwargs.get("uuid"))
        MORCoreService().specificatie_verwijderen(self.kwargs.get("uuid"))
        if response_detail.get("error"):
            messages.error(self.request, "De specificatie is verwijderd mislukt")
        else:
            messages.success(
                request,
                f"De specificatie '{response_detail.get('naam')}' is verwijderd",
            )
        return redirect(reverse("specificatie_lijst"))


class SpecificatieTerughalenView(PermissionRequiredMixin, View):
    permission_required = "authorisatie.specificatie_terughalen"

    def get(self, request, *args, **kwargs):
        response_detail = MORCoreService().specificatie_detail(self.kwargs.get("uuid"))
        MORCoreService().specificatie_terughalen(self.kwargs.get("uuid"))
        messages.success(
            request,
            f"De specificatie '{response_detail.get('naam')}' is teruggehaald",
        )
        return redirect(reverse("specificatie_lijst"))


class TaakopdrachtTaakAanmakenIssueLijstView(PermissionRequiredMixin, FormView):
    permission_required = (
        "authorisatie.taakopdrachten_taak_aanmaken_issue_lijst_bekijken"
    )
    template_name = (
        "beheer/taakopdrachten_taak_aanmaken_issues/taakopdrachten_lijst.html"
    )
    form_class = TaakopdrachtTaakAanmakenIssueLijstForm
    success_url = reverse_lazy("taakopdrachten_taak_aanmaken_issues")
    taakopdracht_choices = []
    page_size = 100
    page = "1"
    page_session_key = "taakopdrachten_taak_aanmaken_issues__page"
    q_session_key = "taakopdrachten_taak_aanmaken_issues__q"

    def get(self, request, *args, **kwargs):
        return HttpResponse("taakopdrachten_taak_aanmaken_issues")
        # return super().get(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        taakapplicaties_response = MORCoreService().applicaties(
            params={"applicatie_type": "taakapplicatie"}, cache_timeout=60 * 60
        )
        page = int(self.request.session.get(self.page_session_key, "1"))
        q = self.request.session.get(self.q_session_key, "")
        params = {
            "limit": self.page_size,
            "q": q,
            "offset": (page - 1) * self.page_size,
            "is_not_afgesloten": True,
            "is_not_verwijderd": True,
            "has_no_taak_url": True,
            "task_taak_aanmaken_status": [
                "geen_task",
                "FAILURE",
                "SUCCESS",
            ],
        }
        taakopdrachten_response = MORCoreService().taakopdrachten(params=params)

        if taakapplicaties_response.get("error"):
            raise Exception(taakapplicaties_response.get("error"))
        if taakopdrachten_response.get("error"):
            raise Exception(taakopdrachten_response.get("error"))

        taakapplicaties_by_url = {
            taakapplicatie.get("_links").get("self"): taakapplicatie.get("naam")
            for taakapplicatie in taakapplicaties_response["results"]
        }

        taakopdrachten_response_results = [
            taakopdracht
            | {
                "applicatie_naam": taakapplicaties_by_url.get(
                    taakopdracht.get("_links").get("applicatie"),
                    "Applicatie niet gevonden",
                )
            }
            for taakopdracht in taakopdrachten_response["results"]
        ]

        self.taakopdracht_choices = [
            (
                taakopdracht["uuid"],
                taakopdracht,
            )
            for taakopdracht in taakopdrachten_response_results
        ]
        self.taakopdracht_count = taakopdrachten_response["count"]
        # self.initial.update(
        #     {
        #         "page": page,
        #         "q": q,
        #     }
        # )

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                "taakopdracht_choices": self.taakopdracht_choices,
                "page_choices": [
                    (p + 1, p + 1)
                    for p in range(math.ceil(self.taakopdracht_count / self.page_size))
                ],
            }
        )
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "count": self.taakopdracht_count,
            }
        )
        return context

    def form_valid(self, form):
        q = form.cleaned_data.get("q") if form.cleaned_data.get("q") else ""
        page = (
            int(form.cleaned_data.get("page", "1"))
            if form.cleaned_data.get("page")
            else 1
        )
        q_changed = q != self.request.session.get(self.q_session_key)
        self.request.session[self.q_session_key] = q
        self.request.session[self.page_session_key] = page if not q_changed else 1

        herstart_taak_aanmaken_taakopdrachten_response = (
            MORCoreService().herstart_task_taak_aanmaken(
                taakopdracht_uuids=form.cleaned_data["taakopdrachten"]
            )
        )

        if herstart_taak_aanmaken_taakopdrachten_response.get("error"):
            raise Exception(herstart_taak_aanmaken_taakopdrachten_response.get("error"))
        return super().form_valid(form)
