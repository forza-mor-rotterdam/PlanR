import json
import logging

from apps.context.utils import get_gebruiker_context
from apps.main.forms import (
    InformatieToevoegenForm,
    LocatieAanpassenForm,
    MeldingAanmakenForm,
    MeldingAfhandelenForm,
    MeldingAnnulerenForm,
    MeldingHeropenenForm,
    MeldingHervattenForm,
    MeldingPauzerenForm,
    MeldingSpoedForm,
    TaakStartenForm,
    TaakVerwijderenForm,
    TakenAanmakenFormset,
)
from apps.main.messages import (
    MELDING_AFHANDELEN_ERROR,
    MELDING_AFHANDELEN_SUCCESS,
    MELDING_ANNULEREN_ERROR,
    MELDING_ANNULEREN_SUCCESS,
    MELDING_HEROPENEN_ERROR,
    MELDING_HEROPENEN_SUCCESS,
    MELDING_HERVATTEN_ERROR,
    MELDING_HERVATTEN_SUCCESS,
    MELDING_INFORMATIE_TOEVOEGEN_ERROR,
    MELDING_INFORMATIE_TOEVOEGEN_SUCCESS,
    MELDING_LOCATIE_AANPASSEN_ERROR,
    MELDING_LOCATIE_AANPASSEN_SUCCESS,
    MELDING_NIET_GEVONDEN_ERROR,
    MELDING_OPHALEN_ERROR,
    MELDING_PAUZEREN_ERROR,
    MELDING_PAUZEREN_SUCCESS,
    MELDING_URGENTIE_AANPASSEN_ERROR,
    MELDING_URGENTIE_AANPASSEN_SUCCESS,
    TAAK_UITZETTEN_ERROR,
    TAAK_UITZETTEN_SUCCESS,
    TAAK_VERWIJDEREN_ERROR,
    TAAK_VERWIJDEREN_SUCCESS,
)
from apps.main.models import MeldingAfhandelreden, StandaardExterneOmschrijving
from apps.main.services import MORCoreService, TaakRService
from apps.main.utils import (
    Logboek,
    get_url_from_links,
    melding_locaties,
    melding_taken,
    publiceer_topic_met_subscriptions,
    to_base64,
)
from apps.main.views.mixins import StreamViewMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.files.storage import default_storage
from django.core.validators import URLValidator
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import FormView, TemplateView
from django.views.generic.base import ContextMixin

logger = logging.getLogger(__name__)


class MeldingDetailViewMixin(ContextMixin):
    def get_melding_detail_context(self, **kwargs):
        mor_core_service = MORCoreService()
        gebruiker_context = get_gebruiker_context(self.request.user)
        melding = mor_core_service.get_melding(self.kwargs.get("id"))
        kwargs = {}
        if isinstance(melding, dict) and melding.get("error"):
            status_code = melding.get("error", {}).get("status_code")
            if status_code == 404:
                messages.error(
                    request=self.request, message=MELDING_NIET_GEVONDEN_ERROR
                )
            else:
                messages.error(request=self.request, message=MELDING_OPHALEN_ERROR)
            melding = {}
        kwargs.update(
            {
                "melding": melding,
                "locaties": melding_locaties(melding),
                "taken": melding_taken(melding),
                "gebruiker_context": gebruiker_context,
            }
        )
        context = super().get_context_data(**kwargs)
        return context


class MeldingDetailTaaktypeViewMixin(MeldingDetailViewMixin):
    def get_taakr_taaktypes_actief(self, taakr_taaktypes):
        return [tt for tt in taakr_taaktypes if tt["actief"]]

    def get_taakr_taaktypes_in_context(self, taakr_taaktypes, context_taaktypes=[]):
        return [
            tt
            for tt in taakr_taaktypes
            if tt["_links"]["taakapplicatie_taaktype_url"] in context_taaktypes
        ]

    def get_taakpplicatie_taaktype_urls_ingebruik(self, taakopdrachten_voor_melding):
        return [
            *set(
                list(
                    to["taaktype"]
                    for to in taakopdrachten_voor_melding
                    if not to["resolutie"] and not to["verwijderd_op"]
                )
            )
        ]

    def get_taakr_taaktypes_niet_ingebruik(
        self, taakr_taaktypes, taakpplicatie_taaktype_urls_ingebruik
    ):
        return [
            tt
            for tt in taakr_taaktypes
            if tt["taakapplicatie_taaktype_url"]
            not in taakpplicatie_taaktype_urls_ingebruik
        ]

    def get_taakr_taaktypes_met_afdelingen(
        self, taakr_taaktypes, afdeling_middels_afdeling_url
    ):
        return sorted(
            [
                tt
                | {
                    "afdelingen": [
                        {
                            k: v
                            for k, v in afdeling_middels_afdeling_url[afdeling].items()
                            if k != "taaktypes_voor_afdelingen"
                        }
                        for afdeling in tt["afdelingen"]
                    ],
                    "verantwoordelijke_afdeling": {
                        k: v
                        for k, v in afdeling_middels_afdeling_url[
                            tt["verantwoordelijke_afdeling"]
                        ].items()
                        if k != "taaktypes_voor_afdelingen"
                    }
                    if tt["verantwoordelijke_afdeling"]
                    else tt["verantwoordelijke_afdeling"],
                }
                for tt in taakr_taaktypes
            ],
            key=lambda b: b["omschrijving"].lower(),
        )

    def get_afdelingen_met_taakr_taaktypes(self, afdelingen, taakr_taaktypes):
        afdelingen = sorted(
            [
                {
                    "afdeling": afdeling,
                    "taakr_taaktypes": sorted(
                        [
                            tt
                            for tt in taakr_taaktypes
                            if tt["_links"]["self"]
                            in [
                                afdeling_tt["_links"]["self"]
                                for afdeling_tt in afdeling["taaktypes_voor_afdelingen"]
                            ]
                        ],
                        key=lambda b: b["omschrijving"].lower(),
                    ),
                }
                for afdeling in afdelingen
            ],
            key=lambda b: b["afdeling"]["naam"].lower(),
        )
        afdelingen_met_taakr_taaktypes = [
            afdeling for afdeling in afdelingen if afdeling["taakr_taaktypes"]
        ]
        return afdelingen_met_taakr_taaktypes

    def get_taakr_taaktypes_zonder_afdelingen(self, taakr_taaktypes):
        return sorted(
            [tt for tt in taakr_taaktypes if not tt["afdelingen"]],
            key=lambda b: b["omschrijving"].lower(),
        )

    def get_taakr_taaktypes_voor_onderwerpen(self, taakr_taaktypes, onderwerp_urls):
        return sorted(
            [
                tt
                for tt in taakr_taaktypes
                if set(tt["gerelateerde_onderwerpen"]).intersection(onderwerp_urls)
            ],
            key=lambda b: b["omschrijving"].lower(),
        )

    def get_melding_detail_taaktype_context(self, **kwargs):
        context = super().get_melding_detail_context(**kwargs)
        melding = context["melding"]
        gebruiker_context = context["gebruiker_context"]

        if not melding:
            return context

        taakopdrachten_voor_melding = melding.get("taakopdrachten_voor_melding", [])
        melding_onderwerp_urls = set(melding.get("onderwerpen", []))

        taakr_service = TaakRService()
        taakr_taaktypes = taakr_service.get_taaktypes()
        afdelingen = taakr_service.get_afdelingen()

        taakr_taaktypes_via_taakapplicatie_taaktype_url = {
            taakr_taaktype["_links"]["taakapplicatie_taaktype_url"]: taakr_taaktype
            for taakr_taaktype in taakr_taaktypes
        }

        afdeling_middels_afdeling_url = {
            afdeling.get("_links", {}).get("self"): afdeling for afdeling in afdelingen
        }
        # filter actieve taakr taaktypes
        taakr_taaktypes_actief = self.get_taakr_taaktypes_actief(taakr_taaktypes)
        # filter taakr taaktypes in gebruiker context(rol)
        taakr_taaktypes_in_context = self.get_taakr_taaktypes_in_context(
            taakr_taaktypes_actief, gebruiker_context.taaktypes
        )
        # taakapplicatie taaktype urls huidige melding
        taakpplicatie_taaktype_urls_ingebruik = (
            self.get_taakpplicatie_taaktype_urls_ingebruik(taakopdrachten_voor_melding)
        )
        # filter taakr taaktypes nof niet ingebruik in huidige melding
        taakr_taaktypes_niet_ingebruik = self.get_taakr_taaktypes_niet_ingebruik(
            taakr_taaktypes_in_context, taakpplicatie_taaktype_urls_ingebruik
        )

        taakr_taaktypes_niet_ingebruik_met_afdelingen = (
            self.get_taakr_taaktypes_met_afdelingen(
                taakr_taaktypes_niet_ingebruik, afdeling_middels_afdeling_url
            )
        )
        afdelingen_met_taakr_taaktypes_niet_ingebruik = (
            self.get_afdelingen_met_taakr_taaktypes(
                afdelingen, taakr_taaktypes_niet_ingebruik
            )
        )

        taakr_taaktypes_voor_onderwerpen = self.get_taakr_taaktypes_voor_onderwerpen(
            taakr_taaktypes_niet_ingebruik, melding_onderwerp_urls
        )
        taakr_taaktypes_zonder_afdelingen = self.get_taakr_taaktypes_zonder_afdelingen(
            taakr_taaktypes_niet_ingebruik
        )
        if taakr_taaktypes_zonder_afdelingen:
            afdelingen_met_taakr_taaktypes_niet_ingebruik.append(
                {
                    "afdeling": {"naam": "Overige"},
                    "taakr_taaktypes": taakr_taaktypes_zonder_afdelingen,
                }
            )
        if taakr_taaktypes_voor_onderwerpen:
            afdelingen_met_taakr_taaktypes_niet_ingebruik.insert(
                0,
                {
                    "afdeling": {"naam": "Taak suggesties"},
                    "taakr_taaktypes": taakr_taaktypes_voor_onderwerpen,
                },
            )

        if context.get("taken"):
            alle_taken = context.get("taken", {}).get("alle_taken")
            alle_taken = [
                taakr_taaktypes_via_taakapplicatie_taaktype_url.get(
                    taak["taaktype"], {}
                )
                | taak
                | {
                    "taakr_taaktype": taakr_taaktypes_via_taakapplicatie_taaktype_url.get(
                        taak["taaktype"], {}
                    )
                    .get("_links", {})
                    .get("self")
                }
                for taak in alle_taken
            ]
            alle_taken = [
                taak
                | {
                    "verantwoordelijke_afdeling": afdeling_middels_afdeling_url[
                        taak["verantwoordelijke_afdeling"]
                    ]
                    if taak.get("verantwoordelijke_afdeling")
                    else None,
                    "afdelingen": [
                        afdeling_middels_afdeling_url[afdeling]
                        for afdeling in taak.get("afdelingen", [])
                    ],
                }
                for taak in alle_taken
            ]
            context["taken"]["alle_taken"] = alle_taken
            context["taken"]["niet_verwijderde_taken"] = [
                taak for taak in alle_taken if not taak["verwijderd_op"]
            ]
            context["taken"]["openstaande_taken"] = [
                taak
                for taak in alle_taken
                if not taak["verwijderd_op"] and not taak["afgesloten_op"]
            ]

        context.update(
            {
                "afdelingen_met_taakr_taaktypes_niet_ingebruik": afdelingen_met_taakr_taaktypes_niet_ingebruik,
                "taakr_taaktypes_niet_ingebruik_met_afdelingen": taakr_taaktypes_niet_ingebruik_met_afdelingen,
            }
        )
        return context


class MeldingDetail(
    MeldingDetailTaaktypeViewMixin, PermissionRequiredMixin, TemplateView
):
    template_name = "melding/melding_detail.html"
    permission_required = "authorisatie.melding_bekijken"

    def request_next_data(self):
        return (
            self.request.GET.get("melding_ids")
            and self.request.GET.get("offset")
            and self.request.GET.get("melding_count")
        )

    def get_context_data(self, **kwargs):
        next_data = self.request_next_data()
        if next_data:
            self.request.session["pagina_melding_ids"] = self.request.GET.get(
                "melding_ids"
            ).split(",")
            self.request.session["offset"] = int(self.request.GET.get("offset"))
            self.request.session["melding_count"] = int(
                self.request.GET.get("melding_count")
            )
            return {}

        context = super().get_melding_detail_taaktype_context(**kwargs)
        melding = context["melding"]
        if not melding:
            return context

        try:
            index = self.request.session.get("pagina_melding_ids", []).index(
                str(self.kwargs.get("id"))
            )
        except Exception:
            index = -1

        meldingen_index = (
            int(self.request.session.get("offset", 0)) + index + 1
            if index >= 0
            else None
        )

        context.update(
            {
                "meldingen_index": meldingen_index,
            }
        )
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_melding_detail_taaktype_context(**kwargs)
        if not context.get("meldingen_index") and self.request_next_data():
            return redirect(reverse("melding_detail", args=[self.kwargs.get("id")]))
        return self.render_to_response(context)


@login_required
@permission_required("authorisatie.melding_bekijken", raise_exception=True)
def publiceer_topic(request, id):
    publiceer_topic_met_subscriptions(reverse("melding_detail", args=[id]))
    return JsonResponse({})


class MeldingAfhandelenView(
    MeldingDetailViewMixin, StreamViewMixin, PermissionRequiredMixin, FormView
):
    permission_required = "authorisatie.melding_afhandelen"
    template_name = "melding/detail/melding_afhandelen_form.html"
    form_class = MeldingAfhandelenForm

    def get_context_data(self, **kwargs):
        context = super().get_melding_detail_context(**kwargs)

        standaard_externe_omschrijving_lijst = (
            StandaardExterneOmschrijving.objects.exclude(
                zichtbaarheid="verbergen"
            ).values(
                "id", "titel", "tekst", "zichtbaarheid", "reden", "specificatie_opties"
            )
        )
        melding_afhandelreden_lijst = MeldingAfhandelreden.objects.values(
            "id", "specificatie_opties"
        )
        self.initial = {"resolutie": self.voorlopige_melding_resolutie(context)}
        context.update(
            {
                "form": self.get_form(),
                "standaard_externe_omschrijving_lijst": list(
                    standaard_externe_omschrijving_lijst
                ),
                "melding_afhandelreden_lijst": list(melding_afhandelreden_lijst),
            }
        )

        return context

    def voorlopige_melding_resolutie(self, context):
        OPGELOST = "opgelost"
        NIET_OPGELOST = "niet_opgelost"
        if (
            len(context["taken"]["opgeloste_taken"])
            == len(context["taken"]["niet_verwijderde_taken"])
            and len(context["taken"]["opgeloste_taken"]) > 0
        ):
            return OPGELOST
        if not context["taken"]["alle_taken"]:
            return NIET_OPGELOST
        if not context["taken"]["niet_verwijderde_taken"]:
            return NIET_OPGELOST
        if context["taken"]["niet_opgeloste_taken"]:
            return NIET_OPGELOST
        if context["taken"]["open_taken"]:
            return NIET_OPGELOST
        return OPGELOST

    def form_valid(self, form):
        mor_core_service = MORCoreService()
        niet_opgelost_reden = form.cleaned_data.get("niet_opgelost_reden")
        response = mor_core_service.melding_afhandelen_v2(
            self.kwargs.get("id"),
            resolutie=form.cleaned_data.get("resolutie"),
            afhandelreden=niet_opgelost_reden.reden if niet_opgelost_reden else None,
            specificatie=form.cleaned_data.get("specificatie"),
            omschrijving_extern=form.cleaned_data.get("omschrijving_extern"),
            omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
            gebruiker=self.request.user.email,
        )
        if response.get("error"):
            messages.error(request=self.request, message=MELDING_AFHANDELEN_ERROR)
        else:
            messages.success(request=self.request, message=MELDING_AFHANDELEN_SUCCESS)
        context = self.get_context_data()
        context.pop("form", None)
        return render(
            self.request,
            "melding/detail/melding_afhandelen_success.html",
            context=context,
        )


@login_required
@permission_required("authorisatie.melding_annuleren", raise_exception=True)
def melding_annuleren(request, id):
    mor_core_service = MORCoreService()
    melding = mor_core_service.get_melding(id)
    if isinstance(melding, dict) and melding.get("error"):
        messages.error(request=request, message=MELDING_OPHALEN_ERROR)
        return render(
            request,
            "melding/melding_actie_form.html",
        )

    form = MeldingAnnulerenForm()
    if request.POST:
        form = MeldingAnnulerenForm(request.POST)
        if form.is_valid():
            bijlagen = request.FILES.getlist("bijlagen", [])
            bijlagen_base64 = []
            for f in bijlagen:
                file_name = default_storage.save(f.name, f)
                bijlagen_base64.append({"bestand": to_base64(file_name)})

            response = mor_core_service.melding_annuleren(
                id,
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                bijlagen=bijlagen_base64,
                gebruiker=request.user.email,
            )
            if isinstance(response, dict) and response.get("error"):
                messages.error(request=request, message=MELDING_ANNULEREN_ERROR)
            else:
                messages.success(request=request, message=MELDING_ANNULEREN_SUCCESS)
            return redirect("melding_detail", id=id)

    return render(
        request,
        "melding/detail/melding_annuleren.html",
        {
            "form": form,
            "melding": melding,
        },
    )


@login_required
@permission_required("authorisatie.melding_heropenen", raise_exception=True)
def melding_heropenen(request, id):
    mor_core_service = MORCoreService()
    melding = mor_core_service.get_melding(id)
    if isinstance(melding, dict) and melding.get("error"):
        messages.error(request=request, message=MELDING_OPHALEN_ERROR)
        return render(
            request,
            "melding/melding_actie_form.html",
        )

    form = MeldingHeropenenForm()
    if request.POST:
        form = MeldingHeropenenForm(request.POST)
        if form.is_valid():
            response = mor_core_service.melding_heropenen(
                id,
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                gebruiker=request.user.email,
            )
            if isinstance(response, dict) and response.get("error"):
                messages.error(request=request, message=MELDING_HEROPENEN_ERROR)
            else:
                messages.success(request=request, message=MELDING_HEROPENEN_SUCCESS)
            return redirect("melding_detail", id=id)

    return render(
        request,
        "melding/detail/melding_heropenen.html",
        {
            "form": form,
            "melding": melding,
        },
    )


@login_required
@permission_required("authorisatie.melding_pauzeren", raise_exception=True)
def melding_pauzeren(request, id):
    mor_core_service = MORCoreService()
    melding = mor_core_service.get_melding(id)
    if isinstance(melding, dict) and melding.get("error"):
        messages.error(request=request, message=MELDING_OPHALEN_ERROR)
        return render(
            request,
            "melding/melding_actie_form.html",
        )

    form = MeldingPauzerenForm()
    actieve_taken = [
        taakopdracht
        for taakopdracht in melding.get("taakopdrachten_voor_melding", [])
        if taakopdracht.get("status", {}).get("naam")
        not in {"voltooid", "voltooid_met_feedback"}
        and not taakopdracht.get("verwijderd_op")
    ]
    if request.POST:
        form = MeldingPauzerenForm(request.POST)
        if form.is_valid():
            response = mor_core_service.melding_status_aanpassen(
                id,
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                gebruiker=request.user.email,
                status=form.cleaned_data.get("status"),
            )
            if isinstance(response, dict) and response.get("error"):
                messages.error(request=request, message=MELDING_PAUZEREN_ERROR)
            else:
                messages.success(request=request, message=MELDING_PAUZEREN_SUCCESS)
            return redirect("melding_detail", id=id)

    return render(
        request,
        "melding/detail/melding_pauzeren.html",
        {
            "form": form,
            "melding": melding,
            "actieve_taken": actieve_taken,
        },
    )


@login_required
@permission_required("authorisatie.melding_hervatten", raise_exception=True)
def melding_hervatten(request, id):
    mor_core_service = MORCoreService()
    melding = mor_core_service.get_melding(id)
    if isinstance(melding, dict) and melding.get("error"):
        messages.error(request=request, message=MELDING_OPHALEN_ERROR)
        return render(
            request,
            "melding/melding_actie_form.html",
        )

    form = MeldingHervattenForm()

    if request.POST:
        form = MeldingHervattenForm(request.POST)
        if form.is_valid():
            response = mor_core_service.melding_status_aanpassen(
                id,
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                gebruiker=request.user.email,
                status="openstaand",
            )
            if isinstance(response, dict) and response.get("error"):
                messages.error(request=request, message=MELDING_HERVATTEN_ERROR)
            else:
                messages.success(request=request, message=MELDING_HERVATTEN_SUCCESS)
            return redirect("melding_detail", id=id)

    return render(
        request,
        "melding/detail/melding_hervatten.html",
        {
            "form": form,
            "melding": melding,
        },
    )


@login_required
@permission_required("authorisatie.melding_spoed_veranderen", raise_exception=True)
def melding_spoed_veranderen(request, id):
    mor_core_service = MORCoreService()
    melding = mor_core_service.get_melding(id)
    if isinstance(melding, dict) and melding.get("error"):
        messages.error(request=request, message=MELDING_OPHALEN_ERROR)
        return render(
            request,
            "melding/melding_actie_form.html",
        )
    form = MeldingSpoedForm(
        initial={"urgentie": 0.5 if melding.get("urgentie", 0.2) == 0.2 else 0.2}
    )

    if request.POST:
        form = MeldingSpoedForm(request.POST)
        if form.is_valid():
            response = mor_core_service.melding_spoed_aanpassen(
                id,
                urgentie=form.cleaned_data.get("urgentie"),
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                gebruiker=request.user.email,
            )
            if isinstance(response, dict) and response.get("error"):
                messages.error(
                    request=request, message=MELDING_URGENTIE_AANPASSEN_ERROR
                )
            else:
                messages.success(
                    request=request, message=MELDING_URGENTIE_AANPASSEN_SUCCESS
                )
            return redirect("melding_detail", id=id)

    return render(
        request,
        "melding/detail/melding_spoed_veranderen.html",
        {
            "form": form,
            "melding": melding,
        },
    )


class TakenAanmakenView(
    MeldingDetailTaaktypeViewMixin, StreamViewMixin, PermissionRequiredMixin, FormView
):
    form_class = TakenAanmakenFormset
    template_name = "melding/detail/taken_aanmaken.html"
    permission_required = "authorisatie.taak_aanmaken"

    def get_context_data(self, **kwargs):
        context = super().get_melding_detail_taaktype_context(**kwargs)
        return context

    def get_success_url(self):
        return reverse("taken_aanmaken", args=[self.kwargs.get("id")])


class TakenAanmakenStreamView(TakenAanmakenView):
    template_name = "melding/detail/taken_aanmaken_stream.html"
    permission_required = "authorisatie.taak_aanmaken"

    def form_invalid(self, form):
        logger.error("TakenAanmakenStreamView errors: FORM INVALID")
        logger.error(form.errors)
        logger.error(form.non_form_errors().as_json())

        messages.error(
            request=self.request,
            message="De taken konden niet worden aangemaakt",
        )
        context = self.get_melding_detail_taaktype_context()
        context.pop("form", None)
        return self.render_to_response(context)

    def form_valid(self, form):
        taken = [
            taak | {"parents": json.loads(taak["parents"])}
            for taak in form.cleaned_data
        ]
        url_validator = URLValidator()
        mor_core_service = MORCoreService()
        taak_aanmaken_api_fields = [
            "melding_uuid",
            "titel",
            "taakapplicatie_taaktype_url",
            "bericht",
            "gebruiker",
        ]
        max_loops = 1000
        loop_counter = 0
        while [
            taak for taak in taken if not taak.get("done")
        ] and loop_counter < max_loops:
            loop_counter += 1
            for taak in taken:
                urls = None
                try:
                    [url for url in taak["parents"] if url_validator(url)]
                    urls = taak["parents"]
                except Exception:
                    ...
                if urls is not None:
                    taak_data = {
                        k: v for k, v in taak.items() if k in taak_aanmaken_api_fields
                    } | {
                        "afhankelijkheid": [
                            {
                                "taakopdracht_url": url,
                            }
                            for url in urls
                        ]
                    }
                    response = mor_core_service.taak_aanmaken(**taak_data)
                    taakopdracht_url = response.get("_links", {}).get("self")
                    taakopdracht_url = (
                        taakopdracht_url.get("href")
                        if isinstance(taakopdracht_url, dict)
                        else taakopdracht_url
                    )
                    if response.get("errors"):
                        messages.error(
                            request=self.request,
                            message=f"De taak '{taak['titel']}' kon niet worden aangemaakt",
                        )
                    elif taakopdracht_url:
                        messages.success(
                            request=self.request,
                            message=f"De taak '{taak['titel']}' is aangemaakt",
                        )
                        for t in [tt for tt in taken if taak["uuid"] in tt["parents"]]:
                            t["parents"] = list(
                                map(
                                    lambda x: taakopdracht_url
                                    if x == taak["uuid"]
                                    else x,
                                    t["parents"],
                                )
                            )
                    taak["done"] = True

        for taak in taken:
            logger.info(taak["titel"])
            logger.info(taak["parents"])
            logger.info("")

        context = self.get_melding_detail_taaktype_context()
        context.pop("form", None)
        return self.render_to_response(context)


@login_required
@permission_required("authorisatie.taak_verwijderen", raise_exception=True)
def taak_verwijderen(request, melding_uuid, taakopdracht_uuid=None):
    mor_core_service = MORCoreService()

    melding = mor_core_service.get_melding(melding_uuid)
    if isinstance(melding, dict) and melding.get("error"):
        messages.error(request=request, message=MELDING_OPHALEN_ERROR)
        return render(
            request,
            "melding/melding_actie_form.html",
        )

    open_taakopdrachten = melding_taken(melding).get("open_taken")
    taakopdracht_urls = {
        taakopdracht.get("uuid"): taakopdracht.get("_links", {}).get("self")
        for taakopdracht in open_taakopdrachten
    }
    taakopdracht = (
        [to for to in open_taakopdrachten if to["uuid"] == str(taakopdracht_uuid)]
        or [{}]
    )[0]
    taakopdracht_opties = [
        (taakopdracht.get("uuid"), taakopdracht.get("titel"))
        for taakopdracht in open_taakopdrachten
        if (taakopdracht_uuid and taakopdracht.get("uuid") == str(taakopdracht_uuid))
        or not taakopdracht_uuid
    ]
    form = TaakVerwijderenForm(taakopdracht_opties=taakopdracht_opties)
    if request.POST:
        form = TaakVerwijderenForm(
            request.POST, taakopdracht_opties=taakopdracht_opties
        )
        if form.is_valid():
            response = mor_core_service.taakopdracht_verwijderen(
                taakopdracht_url=taakopdracht_urls.get(
                    form.cleaned_data.get("taakopdracht")
                ),
                gebruiker=request.user.email,
            )
            if isinstance(response, dict) and response.get("error"):
                messages.error(request=request, message=TAAK_VERWIJDEREN_ERROR)
            else:
                messages.success(request=request, message=TAAK_VERWIJDEREN_SUCCESS)
            return redirect("melding_detail", id=melding_uuid)
    return render(
        request,
        "melding/detail/taak_verwijderen.html",
        {
            "form": form,
            "melding": melding,
            "taakopdracht": taakopdracht,
        },
    )


class TakenStartenView(
    MeldingDetailTaaktypeViewMixin, StreamViewMixin, PermissionRequiredMixin, FormView
):
    template_name = "melding/detail/taak_starten.html"
    permission_required = "authorisatie.taak_starten"
    form_class = TaakStartenForm
    taakopdrachten = None

    def dispatch(self, request, *args, **kwargs):
        context = super().get_melding_detail_context(**kwargs)
        self.melding = context["melding"]
        taakopdracht_uuid = self.kwargs.get("taakopdracht_uuid")
        self.taakopdrachten = [
            taakopdracht
            for taakopdracht in context["taken"]["in_de_wacht_taken"]
            if taakopdracht["uuid"] == str(taakopdracht_uuid)
        ]
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.taakopdrachten:
            kwargs.update(
                {
                    "taakopdracht_opties": [
                        (
                            taakopdracht.get("_links", {}).get("self"),
                            taakopdracht.get("titel"),
                        )
                        for taakopdracht in self.taakopdrachten
                    ],
                }
            )
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "taakopdracht": next(iter(self.taakopdrachten), None),
                "melding": self.melding,
            }
        )
        return context

    def form_invalid(self, form):
        logger.error(f"{self.__class__.__name__} form invalid: {form.errors}")
        return super().form_invalid(form)

    def form_valid(self, form):
        context = super().get_melding_detail_taaktype_context()
        print(form.cleaned_data)
        melding_url = get_url_from_links(context["melding"], "self")
        response = MORCoreService().taakopdracht_uitzetten(
            melding_url=melding_url,
            taakopdracht_url=form.cleaned_data["taakopdracht"],
            gebruiker=self.request.user.email,
        )
        if isinstance(response, dict) and response.get("error"):
            messages.error(request=self.request, message=TAAK_UITZETTEN_ERROR)
        else:
            messages.success(request=self.request, message=TAAK_UITZETTEN_SUCCESS)

        context.pop("form", None)
        return self.render_to_response(context)


@login_required
@permission_required("authorisatie.taak_verwijderen", raise_exception=True)
def taak_starten(request, melding_uuid, taakopdracht_uuid=None):
    mor_core_service = MORCoreService()

    melding = mor_core_service.get_melding(melding_uuid)
    if isinstance(melding, dict) and melding.get("error"):
        messages.error(request=request, message=MELDING_OPHALEN_ERROR)
        return render(
            request,
            "melding/melding_actie_form.html",
        )

    open_taakopdrachten = melding_taken(melding).get("open_taken")
    taakopdracht_urls = {
        taakopdracht.get("uuid"): taakopdracht.get("_links", {}).get("self")
        for taakopdracht in open_taakopdrachten
    }
    taakopdracht = (
        [to for to in open_taakopdrachten if to["uuid"] == str(taakopdracht_uuid)]
        or [{}]
    )[0]
    taakopdracht_opties = [
        (taakopdracht.get("uuid"), taakopdracht.get("titel"))
        for taakopdracht in open_taakopdrachten
        if (taakopdracht_uuid and taakopdracht.get("uuid") == str(taakopdracht_uuid))
        or not taakopdracht_uuid
    ]
    form = TaakVerwijderenForm(taakopdracht_opties=taakopdracht_opties)
    if request.POST:
        form = TaakVerwijderenForm(
            request.POST, taakopdracht_opties=taakopdracht_opties
        )
        if form.is_valid():
            response = mor_core_service.taakopdracht_verwijderen(
                taakopdracht_url=taakopdracht_urls.get(
                    form.cleaned_data.get("taakopdracht")
                ),
                gebruiker=request.user.email,
            )
            if isinstance(response, dict) and response.get("error"):
                messages.error(request=request, message=TAAK_VERWIJDEREN_ERROR)
            else:
                messages.success(request=request, message=TAAK_VERWIJDEREN_SUCCESS)
            return redirect("melding_detail", id=melding_uuid)
    return render(
        request,
        "melding/detail/taak_starten.html",
        {
            "form": form,
            "melding": melding,
            "taakopdracht": taakopdracht,
        },
    )


@login_required
@permission_required("authorisatie.melding_bekijken", raise_exception=True)
def informatie_toevoegen(request, id):
    mor_core_service = MORCoreService()
    form = InformatieToevoegenForm()
    if request.method == "POST":
        form = InformatieToevoegenForm(request.POST, request.FILES)
        if form.is_valid():
            opmerking = form.cleaned_data.get("opmerking")
            bijlagen = request.FILES.getlist("bijlagen_extra")
            bijlagen_base64 = []
            for f in bijlagen:
                file_name = default_storage.save(f.name, f)
                bijlagen_base64.append({"bestand": to_base64(file_name)})

            response = mor_core_service.melding_gebeurtenis_toevoegen(
                id,
                bijlagen=bijlagen_base64,
                omschrijving_intern=opmerking,
                gebruiker=request.user.email,
            )
            if isinstance(response, dict) and response.get("error"):
                messages.error(
                    request=request, message=MELDING_INFORMATIE_TOEVOEGEN_ERROR
                )
            else:
                messages.success(
                    request=request, message=MELDING_INFORMATIE_TOEVOEGEN_SUCCESS
                )
            return redirect("melding_detail", id=id)
    return render(
        request,
        "melding/detail/informatie_toevoegen.html",
        {
            "melding_uuid": id,
            "form": form,
        },
    )


@login_required
@permission_required("authorisatie.melding_aanmaken", raise_exception=True)
def melding_aanmaken(request):
    # Temporary initial form data
    initial_form = {
        "straatnaam": "Westerkade",
        "huisnummer": "29",
        "huisletter": "A",
        "toevoeging": "Bis",
        "wijknaam": "Rotterdam Centrum",
        "buurtnaam": "Nieuwe Werk",
        "rd_x": "4.47522318",
        "rd_y": "51.90523667",
        # "onderwerp": ""
        "toelichting": "Dit is een test melding",
        "naam_melder": "Test Melder",
        "terugkoppeling_gewenst": 1,
    }

    if request.POST:
        form = MeldingAanmakenForm(
            request.POST,
            request.FILES,
        )
        bijlagen = request.FILES.getlist("bijlagen", [])
        file_names = []
        for f in bijlagen:
            file_name = default_storage.save(f.name, f)
            file_names.append(file_name)
        is_valid = form.is_valid()
        if is_valid:
            signaal_data = form.signaal_data(file_names)
            signaal_response = MORCoreService().signaal_aanmaken(
                data=signaal_data,
            )
            return redirect(
                reverse(
                    "melding_verzonden",
                    kwargs={"signaal_uuid": signaal_response.get("uuid")},
                )
            )
    else:
        form = MeldingAanmakenForm(initial=initial_form)

    return render(
        request,
        "melding/aanmaken.html",
        {
            "form": form,
        },
    )


@login_required
@permission_required("authorisatie.melding_aanmaken", raise_exception=True)
def melding_verzonden(request, signaal_uuid):
    return render(
        request,
        "melding/verzonden.html",
    )


# Locatie views
@login_required
@permission_required("authorisatie.locatie_aanpassen", raise_exception=True)
def locatie_aanpassen(request, id):
    try:
        mor_core_service = MORCoreService()
        melding = mor_core_service.get_melding(id)
        if isinstance(melding, dict) and melding.get("error"):
            messages.error(request=request, message=MELDING_OPHALEN_ERROR)
            return render(
                request,
                "melding/melding_actie_form.html",
            )
        locatie = None
        locaties = melding_locaties(melding)

        locaties_primair = [
            locatie
            for locatie in locaties.get("adressen", [])
            if locatie.get("primair") and locatie.get("geometrie") is not None
        ]
        highest_gewicht_locatie = max(
            locaties.get("adressen", []), key=lambda locatie: locatie.get("gewicht", 0)
        )
        if locaties_primair:
            locatie = locaties_primair[0]
        if highest_gewicht_locatie and not locatie:
            locatie = highest_gewicht_locatie

        if not locatie:
            messages.error(request=request, message="Geen primaire lokatie gevonden")
            return render(
                request,
                "melding/melding_actie_form.html",
            )
        form_initial = {
            "geometrie": locatie.get("geometrie"),
        }

        form = LocatieAanpassenForm(initial=form_initial)
        if request.POST:
            form = LocatieAanpassenForm(request.POST, initial=form_initial)
            if form.is_valid():
                locatie_data = {
                    "locatie_type": "adres",
                    "geometrie": form.cleaned_data.get("geometrie"),
                    "straatnaam": form.cleaned_data.get("straatnaam"),
                    "postcode": form.cleaned_data.get("postcode"),
                    "huisnummer": form.cleaned_data.get("huisnummer"),
                    "huisletter": form.cleaned_data.get("huisletter"),
                    "toevoeging": form.cleaned_data.get("toevoeging"),
                    "wijknaam": form.cleaned_data.get("wijknaam"),
                    "buurtnaam": form.cleaned_data.get("buurtnaam"),
                    "plaatsnaam": form.cleaned_data.get("plaatsnaam"),
                }

                response = mor_core_service.locatie_aanpassen(
                    id,
                    omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                    locatie=locatie_data,
                    gebruiker=request.user.email,
                )
                if isinstance(response, dict) and response.get("error"):
                    messages.error(
                        request=request, message=MELDING_LOCATIE_AANPASSEN_ERROR
                    )
                else:
                    messages.success(
                        request=request, message=MELDING_LOCATIE_AANPASSEN_SUCCESS
                    )
                return redirect("melding_detail", id=id)

        return render(
            request,
            "melding/detail/locatie_aanpassen.html",
            {
                "form": form,
                "melding": melding,
                "locatie": locatie,
            },
        )
    except MORCoreService.AntwoordFout as e:
        return JsonResponse(
            {"error": str(e)},
            status=getattr(e, "status_code", 500),
        )


class LogboekView(MeldingDetailViewMixin, PermissionRequiredMixin, TemplateView):
    template_name = "logboek/basis.html"
    permission_required = "authorisatie.melding_bekijken"

    def get_context_data(self, **kwargs):
        kwargs = super().get_melding_detail_context(**kwargs)
        kwargs.update(
            {
                "logboek": Logboek(kwargs["melding"], self.request),
            }
        )
        return kwargs
