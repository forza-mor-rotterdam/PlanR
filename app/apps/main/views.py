import base64
import logging
import math
import os
from datetime import datetime

import requests
import weasyprint
from apps.context.constanten import FilterManager
from apps.context.utils import get_gebruiker_context
from apps.instellingen.models import Instelling
from apps.main.constanten import MSB_WIJKEN
from apps.main.forms import (
    TAAK_RESOLUTIE_GEANNULEERD,
    TAAK_STATUS_VOLTOOID,
    FilterForm,
    InformatieToevoegenForm,
    LocatieAanpassenForm,
    MeldingAanmakenForm,
    MeldingAfhandelenForm,
    MeldingAnnulerenForm,
    MeldingHeropenenForm,
    MeldingHervattenForm,
    MeldingPauzerenForm,
    MeldingSpoedForm,
    MSBLoginForm,
    MSBMeldingZoekenForm,
    StandaardExterneOmschrijvingAanmakenForm,
    StandaardExterneOmschrijvingAanpassenForm,
    StandaardExterneOmschrijvingSearchForm,
    TaakAfrondenForm,
    TaakAnnulerenForm,
    TakenAanmakenForm,
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
    MELDING_LIJST_OPHALEN_ERROR,
    MELDING_LOCATIE_AANPASSEN_ERROR,
    MELDING_LOCATIE_AANPASSEN_SUCCESS,
    MELDING_OPHALEN_ERROR,
    MELDING_PAUZEREN_ERROR,
    MELDING_PAUZEREN_SUCCESS,
    MELDING_URGENTIE_AANPASSEN_ERROR,
    MELDING_URGENTIE_AANPASSEN_SUCCESS,
    TAAK_AFRONDEN_ERROR,
    TAAK_AFRONDEN_SUCCESS,
    TAAK_ANNULEREN_ERROR,
    TAAK_ANNULEREN_SUCCESS,
)
from apps.main.models import StandaardExterneOmschrijving
from apps.main.services import MORCoreService, TaakRService
from apps.main.templatetags.gebruikers_tags import get_gebruiker_object_middels_email
from apps.main.utils import (
    get_actieve_filters,
    get_ui_instellingen,
    get_valide_kolom_classes,
    melding_locaties,
    melding_taken,
    publiceer_topic_met_subscriptions,
    set_actieve_filters,
    set_ui_instellingen,
    to_base64,
    update_qd_met_standaard_meldingen_filter_qd,
)
from bs4 import BeautifulSoup
from config.context_processors import general_settings
from deepdiff import DeepDiff
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.files.storage import default_storage
from django.db.models import Q
from django.forms import formset_factory
from django.http import HttpResponse, JsonResponse, QueryDict, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)
from utils.diversen import get_index
from utils.rd_convert import rd_to_wgs

logger = logging.getLogger(__name__)


def http_403(request):
    return render(
        request,
        "403.html",
    )


def http_404(request):
    current_time = datetime.now()
    server_id = os.getenv("APP_ENV", "Onbekend")

    return render(
        request,
        "404.html",
        {
            "current_time": current_time,
            "server_id": server_id,
            "user_agent": request.META.get("HTTP_USER_AGENT", "Onbekend"),
            "path": request.build_absolute_uri(request.path),
        },
    )


def http_500(request):
    current_time = datetime.now()
    server_id = os.getenv("APP_ENV", "Onbekend")

    return render(
        request,
        "500.html",
        {
            "current_time": current_time,
            "server_id": server_id,
            "user_agent": request.META.get("HTTP_USER_AGENT", "Onbekend"),
            "path": request.build_absolute_uri(request.path),
        },
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        if request.user.has_perms(["authorisatie.melding_lijst_bekijken"]):
            return redirect(reverse("melding_lijst"))
        if request.user.has_perms(["authorisatie.beheer_bekijken"]):
            return redirect(reverse("beheer"))
        if request.user.is_authenticated:
            return redirect(reverse("root"), False)

        if settings.OIDC_ENABLED:
            return redirect(f"/oidc/authenticate/?next={request.GET.get('next', '/')}")
        if settings.ENABLE_DJANGO_ADMIN_LOGIN:
            return redirect(f"/admin/login/?next={request.GET.get('next', '/admin')}")

        return HttpResponse("Er is geen login ingesteld")


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("login"), False)

        if settings.OIDC_ENABLED:
            return redirect("/oidc/logout/")
        if settings.ENABLE_DJANGO_ADMIN_LOGIN:
            return redirect(f"/admin/logout/?next={request.GET.get('next', '/')}")

        return HttpResponse("Er is geen logout ingesteld")


# @login_required
def root(request):
    if request.user.has_perms(["authorisatie.melding_lijst_bekijken"]):
        return redirect(reverse("melding_lijst"))
    if request.user.has_perms(["authorisatie.beheer_bekijken"]):
        return redirect(reverse("beheer"))
    return render(
        request,
        "home.html",
        {},
    )


@login_required
@permission_required("authorisatie.melding_lijst_bekijken", raise_exception=True)
def dashboard(request):
    return render(
        request,
        "dashboard/dashboard.html",
        {},
    )


@login_required
def sidesheet_actueel(request):
    return render(
        request,
        "sidesheet/actueel.html",
        {},
    )


@login_required
@permission_required("authorisatie.melding_lijst_bekijken", raise_exception=True)
def melding_lijst(request):
    mor_core_service = MORCoreService()
    gebruiker = request.user
    gebruiker_context = get_gebruiker_context(gebruiker)

    standaard_waardes = {
        "limit": "25",
        "foldout_states": "[]",
    }
    standaard_waardes.update(get_ui_instellingen(gebruiker))
    actieve_filters = get_actieve_filters(gebruiker)

    qs = QueryDict("", mutable=True)
    qs.update(request.GET)

    # remove unused GET vars
    allowed_querystring_params = list(actieve_filters.keys()) + [
        "ordering",
        "q",
        "offset",
    ]
    qs_keys = list(qs.keys())
    [qs.pop(k, None) for k in qs_keys if k not in allowed_querystring_params]

    qs.update(request.POST)

    if qs:
        nieuwe_actieve_filters = {
            k: qs.getlist(k, []) for k, v in actieve_filters.items()
        }
        standaard_waardes.update(
            set_ui_instellingen(
                gebruiker,
                qs.get("ordering", standaard_waardes["ordering"]),
                qs.get("search_with_profiel_context"),
            )
        )
        standaard_waardes["foldout_states"] = qs.get("foldout_states")

        # reset pagination offset if meldingen count most likely will change by changing filters
        if DeepDiff(actieve_filters, nieuwe_actieve_filters) or qs.get(
            "q", ""
        ) != request.session.get("q", ""):
            request.session["offset"] = "0"
        else:
            request.session["offset"] = qs.get("offset", "0")

        if qs.get("q"):
            request.session["q"] = qs.get("q", "")
        elif request.session.get("q"):
            del request.session["q"]

        actieve_filters = set_actieve_filters(gebruiker, nieuwe_actieve_filters)

    standaard_waardes["offset"] = request.session.get("offset", "0")

    form_qs = QueryDict("", mutable=True)
    if request.session.get("q"):
        form_qs.update(
            {
                "q": request.session.get("q"),
            }
        )
    form_qs.update(standaard_waardes)

    for k, v in actieve_filters.items():
        if v:
            form_qs.setlist(k, v)

    meldingen_filter_query_dict = update_qd_met_standaard_meldingen_filter_qd(
        form_qs, gebruiker_context
    )
    meldingen_data = mor_core_service.get_melding_lijst(
        query_string=FilterManager().get_query_string(meldingen_filter_query_dict)
    )
    if (
        len(meldingen_data.get("results", [])) == 0
        and meldingen_filter_query_dict.get("offset") != "0"
    ):
        # reset pagination to first page if meldingen result is empty and the offset is not 0
        meldingen_filter_query_dict["offset"] = "0"
        form_qs["offset"] = "0"
        request.session["offset"] = "0"
        meldingen_data = mor_core_service.get_melding_lijst(
            query_string=FilterManager().get_query_string(meldingen_filter_query_dict)
        )
    if isinstance(meldingen_data, dict) and meldingen_data.get("error"):
        messages.error(request=request, message=MELDING_LIJST_OPHALEN_ERROR)

    request.session["pagina_melding_ids"] = [
        r.get("uuid") for r in meldingen_data.get("results", [])
    ]
    request.session["melding_count"] = meldingen_data.get("count", 0)

    form = FilterForm(
        form_qs,
        gebruiker=gebruiker,
        meldingen_data=meldingen_data,
    )

    form.is_valid()
    if form.errors:
        logger.warning(form.errors)

    return render(
        request,
        "melding/melding_lijst.html",
        {
            "data": meldingen_data,
            "form": form,
            "kolommen": get_valide_kolom_classes(gebruiker_context),
        },
    )


@login_required
@permission_required("authorisatie.melding_bekijken", raise_exception=True)
def melding_detail(request, id):
    mor_core_service = MORCoreService()
    gebruiker_context = get_gebruiker_context(request.user)
    melding = mor_core_service.get_melding(id)
    if isinstance(melding, dict) and melding.get("error"):
        messages.error(request=request, message=MELDING_OPHALEN_ERROR)

    if (
        request.GET.get("melding_ids")
        and request.GET.get("offset")
        and request.GET.get("melding_count")
    ):
        request.session["pagina_melding_ids"] = request.GET.get("melding_ids").split(
            ","
        )
        request.session["offset"] = int(request.GET.get("offset"))
        request.session["melding_count"] = int(request.GET.get("melding_count"))
        return redirect(reverse("melding_detail", args=[id]))

    try:
        index = request.session.get("pagina_melding_ids", []).index(str(id))
    except Exception:
        index = -1
    meldingen_index = (
        int(request.session.get("offset", 0)) + index + 1 if index >= 0 else None
    )
    open_taakopdrachten = melding_taken(melding).get("open_taken")
    locaties = melding_locaties(melding)
    taaktypes = TaakRService(request=request).get_niet_actieve_taaktypes(melding)
    categorized_taaktypes = TaakRService(request=request).categorize_taaktypes(
        melding, taaktypes, context_taaktypes=gebruiker_context.taaktypes
    )
    form = InformatieToevoegenForm()
    overview_querystring = request.session.get("overview_querystring", "")

    return render(
        request,
        "melding/melding_detail.html",
        {
            "melding": melding,
            "locaties": locaties,
            "form": form,
            "overview_querystring": overview_querystring,
            "taaktypes": categorized_taaktypes,
            "open_taakopdrachten": open_taakopdrachten,
            "meldingen_index": meldingen_index,
        },
    )


class LichtmastView(PermissionRequiredMixin, TemplateView):
    template_name = "melding/detail/lichtmast.html"
    permission_required = "authorisatie.melding_bekijken"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lichtmast_id = self.kwargs.get("lichtmast_id")
        url = f"https://ows.gis.rotterdam.nl/cgi-bin/mapserv.exe?map=d:%5Cgwr%5Cwebdata%5Cmapserver%5Cmap%5Cbbdwh_pub.map&service=wfs&version=2.0.0&request=GetFeature&typeNames=namespace:sdo_gwr_bsb_ovl&Filter=<Filter><PropertyIsEqualTo><PropertyName>LICHTPUNT_ID</PropertyName><Literal>{lichtmast_id}</Literal></PropertyIsEqualTo></Filter>"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "xml")
        lichtmast_data = {}
        fields = (
            ("ms:LICHTPUNT_ID", "Lichtmast id"),
            ("ms:LICHTPUNTNUMMER", "Lichtpuntnummer"),
            ("ms:LAMP_ID", "Lamp id"),
            ("ms:STRAAT", "Straat"),
            ("ms:BEHEERDER", "Beheerder"),
            ("ms:EIGENAAR", "Eigenaar"),
            ("ms:AMBITIENIVEAU", "Ambitieniveau"),
            ("ms:LAATSTE_MUTATIE_ARMATUUR", "Laatste mutatie armatuur"),
            ("ms:LAATSTE_MUTATIE_LICHTBRON", "Laatste mutatie lichtbron"),
            ("ms:PLAATSINGSDATUM_LICHTBRON", "Plaatsingsdatum lichtbron"),
            ("ms:IND_IN_STORING", "Storing"),
            ("ms:STORING_OMSCHRIJVINGEN", "Storings omschrijving"),
            ("gml:pos", "rd"),
        )

        lichtmast_data = [
            (f[1], soup.find_all(f[0])[0].text if soup.find_all(f[0]) else "-")
            for f in fields
        ]
        rd_list = (
            lichtmast_data[-1][1].split(" ")
            if len(lichtmast_data[-1][1].split(" ")) == 2
            else []
        )
        rd = [float(xy) for xy in rd_list]
        print(rd)
        lichtmast_data.append(("gps", rd_to_wgs(*rd) if rd else []))
        context.update(
            {
                "lichtmast_data": lichtmast_data,
            }
        )
        return context


@login_required
@permission_required("authorisatie.melding_bekijken", raise_exception=True)
def melding_next(request, id, richting):
    mor_core_service = MORCoreService()
    melding_id = str(id)
    frame_id = "melding_next_volgend" if richting > 0 else "melding_next_vorige"
    label = "Volgende" if richting > 0 else "Vorige"

    pagina_item_aantal = 25
    next_melding_url = None
    pagina = int(request.session.get("offset", "0"))
    melding_count = request.session.get("melding_count", 0)
    laatste_pagina = math.floor(melding_count / pagina_item_aantal)
    gebruiker = request.user
    gebruiker_context = get_gebruiker_context(gebruiker)

    pagina_melding_ids = request.session.get("pagina_melding_ids", [])

    index = get_index(pagina_melding_ids, melding_id)
    if (index == 0 and pagina == 0 and richting < 0) or (
        index == len(pagina_melding_ids) - 1
        and pagina == (laatste_pagina * pagina_item_aantal)
        and richting > 0
    ):
        # eerste of laatste melding in meldingen lijst over alle pagina's
        return render(
            request,
            "melding/melding_next.html",
            {
                "frame_id": frame_id,
            },
        )

    if (index == 0 and richting < 0) or (
        index == pagina_item_aantal - 1 and richting > 0
    ):
        # als huidige melding zich aan het begin of aan het eind van de pagina bevindt, haal dan respectievelijk de vorige of volgende pagina op
        actieve_filters = get_actieve_filters(gebruiker)
        standaard_waardes = {
            "limit": f"{pagina_item_aantal}",
            "q": request.session.get("q", ""),
            "offset": str(
                (int(pagina / pagina_item_aantal) + richting) * pagina_item_aantal
            ),
        }
        standaard_waardes.update(get_ui_instellingen(gebruiker))

        pagina = (int(pagina / pagina_item_aantal) + richting) * pagina_item_aantal
        standaard_waardes["offset"] = str(pagina)

        form_qs = QueryDict("", mutable=True)
        form_qs.update(standaard_waardes)

        for k, v in actieve_filters.items():
            if v:
                form_qs.setlist(k, v)

        meldingen_filter_query_dict = update_qd_met_standaard_meldingen_filter_qd(
            form_qs, gebruiker_context
        )
        meldingen_data = mor_core_service.get_melding_lijst(
            query_string=FilterManager().get_query_string(meldingen_filter_query_dict)
        )
        if isinstance(meldingen_data, dict) and meldingen_data.get("error"):
            messages.error(request=request, message=MELDING_LIJST_OPHALEN_ERROR)

        pagina_melding_ids = [r.get("uuid") for r in meldingen_data.get("results")]
        melding_count = meldingen_data.get("count")
        index = get_index(pagina_melding_ids, melding_id)
        nieuwe_melding_id = None
        if index == -1 and pagina_melding_ids:
            # in de happy flow zal vorige of volgende melding zich op vorige of volgende pagina bevinden
            nieuwe_melding_id = (
                pagina_melding_ids[0] if richting > 0 else pagina_melding_ids[-1]
            )
        if nieuwe_melding_id:
            next_melding_url = f"{reverse('melding_detail', args=[nieuwe_melding_id])}?melding_ids={','.join(pagina_melding_ids)}&offset={pagina}&melding_count={melding_count}"

    elif index != -1:
        next_melding_url = reverse(
            "melding_detail", args=[pagina_melding_ids[index + richting]]
        )

    return render(
        request,
        "melding/melding_next.html",
        {
            "frame_id": frame_id,
            "next_melding_url": next_melding_url,
            "label": label,
            "richting": richting,
        },
    )


@login_required
@permission_required("authorisatie.melding_bekijken", raise_exception=True)
def publiceer_topic(request, id):
    publiceer_topic_met_subscriptions(reverse("melding_detail", args=[id]))
    return JsonResponse({})


@login_required
@permission_required("authorisatie.melding_afhandelen", raise_exception=True)
def melding_afhandelen(request, id):
    mor_core_service = MORCoreService()
    melding = mor_core_service.get_melding(id)
    if isinstance(melding, dict) and melding.get("error"):
        messages.error(request=request, message=MELDING_OPHALEN_ERROR)
        return render(
            request,
            "melding/melding_actie_form.html",
        )

    melding_bijlagen = [
        [
            b
            for b in (
                meldinggebeurtenis.get("taakgebeurtenis", {}).get("bijlagen", [])
                if meldinggebeurtenis.get("taakgebeurtenis")
                else []
            )
        ]
        for meldinggebeurtenis in melding.get("meldinggebeurtenissen", [])
    ]
    benc_user = request.user.profiel.context.template == "benc"
    signaal = (
        melding.get("signalen_voor_melding")[0]
        if melding.get("signalen_voor_melding")
        else {}
    )
    # Als het om een B&C formulier gaat en er geen terugkoppeling gewenst is en/of er geen email bekend is
    standaard_omschrijving_niet_weergeven = bool(
        benc_user
        and (
            signaal.get("meta", {}).get("terugkoppeling_gewenst") != "Ja"
            or not signaal.get("melder", {}).get("email")
        )
    )
    bijlagen_flat = [b for bl in melding_bijlagen for b in bl]
    form = MeldingAfhandelenForm(
        standaard_omschrijving_niet_weergeven=standaard_omschrijving_niet_weergeven
    )
    if request.POST:
        form = MeldingAfhandelenForm(
            request.POST,
            standaard_omschrijving_niet_weergeven=standaard_omschrijving_niet_weergeven,
        )
        if form.is_valid():
            bijlagen = request.FILES.getlist("bijlagen", [])
            bijlagen_base64 = []
            for f in bijlagen:
                file_name = default_storage.save(f.name, f)
                bijlagen_base64.append({"bestand": to_base64(file_name)})

            response = mor_core_service.melding_status_aanpassen(
                id,
                omschrijving_extern=form.cleaned_data.get("omschrijving_extern"),
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                bijlagen=bijlagen_base64,
                gebruiker=request.user.email,
                status="afgehandeld",
                resolutie="opgelost",
            )
            if isinstance(response, dict) and response.get("error"):
                messages.error(request=request, message=MELDING_AFHANDELEN_ERROR)
            else:
                messages.success(request=request, message=MELDING_AFHANDELEN_SUCCESS)
            return redirect("melding_detail", id=id)

    return render(
        request,
        "melding/part_melding_afhandelen.html",
        {
            "form": form,
            "melding": melding,
            "bijlagen": bijlagen_flat,
        },
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

    melding_bijlagen = [
        [
            b
            for b in (
                meldinggebeurtenis.get("taakgebeurtenis", {}).get("bijlagen", [])
                if meldinggebeurtenis.get("taakgebeurtenis")
                else []
            )
        ]
        for meldinggebeurtenis in melding.get("meldinggebeurtenissen", [])
    ]

    bijlagen_flat = [b for bl in melding_bijlagen for b in bl]
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
        "melding/part_melding_annuleren.html",
        {
            "form": form,
            "melding": melding,
            "bijlagen": bijlagen_flat,
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
        "melding/melding_heropenen.html",
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
        "melding/melding_pauzeren.html",
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
        "melding/melding_hervatten.html",
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
        "melding/melding_spoed_veranderen.html",
        {
            "form": form,
            "melding": melding,
        },
    )


class TakenAanmakenView(PermissionRequiredMixin, FormView):
    form_class = formset_factory(TakenAanmakenForm, extra=0)
    template_name = "melding/detail/taken_aanmaken.html"
    permission_required = "authorisatie.taak_aanmaken"

    def get_success_url(self):
        return reverse("taken_aanmaken", args=[self.kwargs.get("id")])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        mor_core_service = MORCoreService()
        gebruiker_context = get_gebruiker_context(self.request.user)
        melding = mor_core_service.get_melding(self.kwargs.get("id"))
        if isinstance(melding, dict) and melding.get("error"):
            messages.error(request=self.request, message=MELDING_OPHALEN_ERROR)
            # return render(
            #     self.request,
            #     "melding/melding_actie_form.html",
            # )

        taakr_service = TaakRService()
        taaktypes_with_afdelingen = taakr_service.get_taaktypes_with_afdelingen(
            melding, context_taaktypes=gebruiker_context.taaktypes
        )
        afdeling_by_url = {
            afdeling.get("_links", {}).get("self"): afdeling.get("naam")
            for afdeling in taakr_service.get_afdelingen()
        }

        # Categorize taaktypes by afdeling and get gerelateerde onderwerpen
        afdelingen = {}
        onderwerp_gerelateerde_taaktypes = []
        melding_onderwerpen = set(melding.get("onderwerpen", []))

        for item in taaktypes_with_afdelingen:
            taaktype = item["taaktype"]
            afdeling = item["afdeling"]
            afdeling_naam = afdeling.get("naam", "Overig")

            taaktype_url = taaktype.get("_links", {}).get("taakapplicatie_taaktype_url")
            taaktype_omschrijving = taaktype.get("omschrijving")

            afdelingen.setdefault(afdeling_naam, []).append(
                (taaktype_url, taaktype_omschrijving)
            )

            gerelateerde_onderwerpen = set(
                item["taaktype"].get("gerelateerde_onderwerpen", [])
            )
            if melding_onderwerpen.intersection(gerelateerde_onderwerpen):
                onderwerp_gerelateerde_taaktypes.append(
                    (taaktype_url, taaktype_omschrijving)
                )

        next(iter(afdelingen.keys()), None)

        afdelingen_taaktypes = [
            (
                afdeling_naam,
                [
                    (taaktype_url, taaktype_omschrijving)
                    for taaktype_url, taaktype_omschrijving in afdeling_taaktypes
                ],
            )
            for afdeling_naam, afdeling_taaktypes in afdelingen.items()
        ]
        afdelingen_taaktypes.sort(key=lambda x: (x[0] == "Overig", x[0]))

        taaktypes = {
            tt.get("taaktype")
            .get("_links")
            .get("taakapplicatie_taaktype_url"): [
                tt.get("taaktype").get("_links").get("taakapplicatie_taaktype_url"),
                tt.get("taaktype").get("omschrijving"),
                tt.get("taaktype").get("_links").get("self"),
                tt.get("taaktype"),
            ]
            for tt in taaktypes_with_afdelingen
        }
        taaktypes = [
            [
                url,
                taaktype[1],
                taaktype[2],
                taaktype[3],
            ]
            for url, taaktype in taaktypes.items()
        ]

        taaktypes.sort(key=lambda x: x[1])
        onderwerp_gerelateerde_taaktypes = list(
            {tt[0]: tt for tt in onderwerp_gerelateerde_taaktypes}.values()
        )
        if onderwerp_gerelateerde_taaktypes:
            afdelingen_taaktypes.insert(
                0, ["Taak suggesties", onderwerp_gerelateerde_taaktypes]
            )

        context.update(
            {
                "afdelingen": afdelingen_taaktypes,
                "afdeling_by_url": afdeling_by_url,
                "taaktypes": taaktypes,
                "melding": melding,
                "locaties": melding_locaties(melding),
            }
        )
        return context


class TakenAanmakenStreamView(TakenAanmakenView):
    template_name = "melding/detail/taken_aanmaken_stream.html"
    permission_required = "authorisatie.taak_aanmaken"

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        response.headers["Content-Type"] = "text/vnd.turbo-stream.html"
        return response

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        response.headers["Content-Type"] = "text/vnd.turbo-stream.html"
        return response

    def form_invalid(self, form):
        logger.error("TakenAanmakenStreamView: FORM INVALID")
        logger.error(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        mor_core_service = MORCoreService()
        responses = [
            taak_data | {"response": mor_core_service.taak_aanmaken(**taak_data)}
            for taak_data in form.cleaned_data
        ]
        for response in responses:
            if response.get("response").get("error"):
                messages.error(
                    request=self.request,
                    message=f"De taak '{response.get('titel')}' kon niet worden aangemaakt",
                )
            else:
                messages.success(
                    request=self.request,
                    message=f"De taak '{response.get('titel')}' is aangemaakt",
                )
        context = self.get_context_data()
        context.pop("form", None)
        return self.render_to_response(context)


@login_required
@permission_required("authorisatie.taak_afronden", raise_exception=True)
def taak_afronden(request, melding_uuid):
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
    taakopdracht_opties = [
        (taakopdracht.get("uuid"), taakopdracht.get("titel"))
        for taakopdracht in open_taakopdrachten
    ]
    form = TaakAfrondenForm(taakopdracht_opties=taakopdracht_opties)
    if request.POST:
        form = TaakAfrondenForm(request.POST, taakopdracht_opties=taakopdracht_opties)

        if form.is_valid():
            bijlagen = request.FILES.getlist("bijlagen", [])
            bijlagen_base64 = []
            for f in bijlagen:
                file_name = default_storage.save(f.name, f)
                bijlagen_base64.append({"bestand": to_base64(file_name)})
            response = mor_core_service.taak_status_aanpassen(
                taakopdracht_url=taakopdracht_urls.get(
                    form.cleaned_data.get("taakopdracht")
                ),
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                bijlagen=bijlagen_base64,
                gebruiker=request.user.email,
                status=TAAK_STATUS_VOLTOOID,
                resolutie=form.cleaned_data.get("resolutie"),
            )
            if isinstance(response, dict) and response.get("error"):
                messages.error(request=request, message=TAAK_AFRONDEN_ERROR)
            else:
                messages.success(request=request, message=TAAK_AFRONDEN_SUCCESS)
            return redirect("melding_detail", id=melding_uuid)

    return render(
        request,
        "melding/part_taak_afronden.html",
        {
            "form": form,
            "melding": melding,
        },
    )


@login_required
@permission_required("authorisatie.taak_annuleren", raise_exception=True)
def taak_annuleren(request, melding_uuid):
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
    taakopdracht_opties = [
        (taakopdracht.get("uuid"), taakopdracht.get("titel"))
        for taakopdracht in open_taakopdrachten
    ]
    form = TaakAnnulerenForm(taakopdracht_opties=taakopdracht_opties)
    if request.POST:
        form = TaakAnnulerenForm(request.POST, taakopdracht_opties=taakopdracht_opties)
        if form.is_valid():
            response = mor_core_service.taak_status_aanpassen(
                taakopdracht_url=taakopdracht_urls.get(
                    form.cleaned_data.get("taakopdracht")
                ),
                status=TAAK_STATUS_VOLTOOID,
                resolutie=TAAK_RESOLUTIE_GEANNULEERD,
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                gebruiker=request.user.email,
                bijlagen=[],
            )
            if isinstance(response, dict) and response.get("error"):
                messages.error(request=request, message=TAAK_ANNULEREN_ERROR)
            else:
                messages.success(request=request, message=TAAK_ANNULEREN_SUCCESS)
            return redirect("melding_detail", id=melding_uuid)
    return render(
        request,
        "melding/part_taak_annuleren.html",
        {
            "form": form,
            "melding": melding,
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
        "melding/part_informatie_toevoegen.html",
        {
            "melding_uuid": id,
            "form": form,
        },
    )


@login_required
@permission_required("authorisatie.medewerker_gegevens_bekijken", raise_exception=True)
def gebruiker_info(request, gebruiker_email):
    gebruiker = get_gebruiker_object_middels_email(gebruiker_email)

    return render(
        request,
        "melding/part_gebruiker_info.html",
        {"gebruiker": gebruiker},
    )


@login_required
@permission_required("authorisatie.melding_bekijken", raise_exception=True)
def melding_pdf_download(request, id):
    mor_core_service = MORCoreService()
    melding = mor_core_service.get_melding(id)
    if isinstance(melding, dict) and melding.get("error"):
        messages.error(request=request, message=MELDING_OPHALEN_ERROR)

    base_url = request.build_absolute_uri()
    path_to_css_file = (
        "/app/frontend/public/build/app.css" if settings.DEBUG else "/static/app.css"
    )
    melding_bijlagen = [
        [bijlage for bijlage in meldinggebeurtenis.get("bijlagen", [])]
        + [
            b
            for b in (
                meldinggebeurtenis.get("taakgebeurtenis", {}).get("bijlagen", [])
                if meldinggebeurtenis.get("taakgebeurtenis")
                else []
            )
        ]
        for meldinggebeurtenis in melding.get("meldinggebeurtenissen", [])
    ]
    bijlagen_flat = [b for bl in melding_bijlagen for b in bl]
    context = {
        "melding": melding,
        "bijlagen_extra": bijlagen_flat,
        "base_url": f"{request.scheme}://{request.get_host()}",
        "request": request,
    }
    context.update(general_settings(request))

    html = render_to_string("pdf/melding.html", context=context)

    pdf = weasyprint.HTML(string=html, base_url=base_url).write_pdf(
        stylesheets=[path_to_css_file]
    )
    pdf_filename = f"serviceverzoek_{id}.pdf"

    return HttpResponse(
        pdf,
        content_type="application/pdf",
        headers={"Content-Disposition": f'attachment;filename="{pdf_filename}"'},
    )


@login_required
@permission_required("authorisatie.melding_bekijken", raise_exception=True)
def meldingen_bestand(request):
    Instelling.actieve_instelling()
    mor_core_service = MORCoreService()
    modified_path = request.path.replace(settings.MOR_CORE_URL_PREFIX, "")
    response = mor_core_service.bestand_halen(modified_path)
    return StreamingHttpResponse(
        response.raw,
        content_type=response.headers.get("content-type"),
        headers={
            "Content-Disposition": "attachment",
        },
        status=response.status_code,
        reason=response.reason,
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


@login_required
@permission_required("authorisatie.msb_toegang", raise_exception=True)
def msb_login(request):
    form = MSBLoginForm()
    errors = None
    if request.POST:
        form = MSBLoginForm(request.POST)
        is_valid = form.is_valid()
        if is_valid:
            msb_base_url = form.cleaned_data.get("omgeving")
            url = f"{msb_base_url}/sbmob/api/login"
            login_data = {
                "uid": form.cleaned_data["gebruikersnummer"],
                "pwd": form.cleaned_data["wachtwoord"],
            }
            response = requests.post(url=url, data=login_data)
            if response.status_code == 200:
                request.session["msb_token"] = response.json().get("result")
                request.session["msb_base_url"] = msb_base_url
                return redirect(reverse("msb_melding_zoeken"))
            logger.error("msb_login error=%s", response.text)
            errors = [response.text]

    return render(request, "msb/login.html", {"form": form, "errors": errors})


@login_required
@permission_required("authorisatie.msb_toegang", raise_exception=True)
def msb_melding_zoeken(request):
    if not request.session.get("msb_token"):
        return redirect(reverse("msb_login"))
    form = MSBMeldingZoekenForm()
    msb_data = request.session.get("msb_melding")
    if request.POST:
        form = MSBMeldingZoekenForm(request.POST)
        is_valid = form.is_valid()
        if is_valid:
            url = f"{request.session['msb_base_url']}/sbmob/api/msb/melding/{form.cleaned_data.get('msb_nummer')}"
            response = requests.get(
                url,
                headers={
                    "Authorization": f"Bearer {request.session.get('msb_token')}",
                },
            )
            if response.status_code == 200:
                msb_data = response.json().get("result", {"test": "test"})
                request.session["msb_melding"] = response.json().get("result")
                return redirect(reverse("msb_melding_zoeken"))
            if response.status_code == 401:
                return redirect(reverse("msb_login"))

            logger.error("msb melding zoeken error=%s", response.text)

    return render(
        request,
        "msb/melding_zoeken.html",
        {
            "form": form,
            "msb_data": msb_data,
        },
    )


@login_required
@permission_required("authorisatie.msb_toegang", raise_exception=True)
def msb_importeer_melding(request):
    instelling = Instelling.actieve_instelling()
    if not request.session.get("msb_token"):
        return redirect(reverse("msb_login"))
    if not request.session.get("msb_melding"):
        return redirect(reverse("msb_melding_zoeken"))
    msb_base_url = request.session["msb_base_url"]

    def _to_base64(binary_file_data):
        base64_encoded_data = base64.b64encode(binary_file_data)
        base64_message = base64_encoded_data.decode("utf-8")
        return base64_message

    msb_data = request.session.get("msb_melding")
    msb_id = msb_data.get("id")
    now = timezone.localtime(timezone.now())
    wijk_buurt = [
        {
            "wijknaam": w.get("omschrijving"),
            "buurtnaam": b.get("omschrijving"),
        }
        for w in MSB_WIJKEN
        for b in w.get("buurten", [])
        if b.get("code") == msb_data.get("locatie", {}).get("buurtNummer")
    ]
    huisnummer = msb_data.get("locatie", {}).get("adres", {}).get("huisnummer")
    huisletter = None
    try:
        huisnummer = int(huisnummer)
    except Exception:
        huisletter = huisnummer
        huisnummer = None

    post_data = {
        "signaal_url": "https://planr.rotterdam.nl/melding/signaal/42",
        "melder": {
            "naam": msb_data.get("melder", {}).get("naam"),
            "email": msb_data.get("melder", {}).get("email"),
            "telefoonnummer": msb_data.get("melder", {}).get("telefoon"),
        },
        "origineel_aangemaakt": msb_data.get("datumMelding", now.isoformat()),
        "onderwerpen": [
            f"{instelling.mor_core_basis_url}/api/v1/onderwerp/grofvuil-op-straat/"
        ],
        "omschrijving_melder": msb_data.get("omschrijving", "")[:500],
        "aanvullende_informatie": msb_data.get("aanvullendeInformatie", "")[:5000],
        "meta": msb_data,
        "meta_uitgebreid": {},
        "adressen": [
            {
                "plaatsnaam": "Rotterdam",
                "straatnaam": msb_data.get("locatie", {})
                .get("adres", {})
                .get("straatNaam"),
            },
        ],
    }
    if huisnummer:
        post_data["adressen"][0]["huisnummer"] = huisnummer
    if huisletter:
        post_data["adressen"][0]["huisletter"] = huisletter

    if wijk_buurt:
        post_data["adressen"][0]["wijknaam"] = wijk_buurt[0].get("wijknaam")
        post_data["adressen"][0]["buurtnaam"] = wijk_buurt[0].get("buurtnaam")
    try:
        wgs = rd_to_wgs(
            msb_data.get("locatie", {}).get("x", 0),
            msb_data.get("locatie", {}).get("y", 0),
        )
        post_data["adressen"][0]["geometrie"] = {
            "type": "Point",
            "coordinates": [wgs[1], wgs[0]],
        }
    except Exception:
        logger.error("rd x=%s", msb_data.get("locatie", {}).get("x", 0))
        logger.error("rd y=%s", msb_data.get("locatie", {}).get("y", 0))

    foto_urls = [f"{msb_base_url}{f.get('url')}" for f in msb_data.get("fotos", [])]

    post_data["bijlagen"] = []
    for f in foto_urls:
        f_response = requests.get(
            url=f,
            headers={
                "Authorization": f"Bearer {request.session.get('msb_token')}",
            },
            stream=True,
        )
        b64 = _to_base64(f_response.content)
        post_data["bijlagen"].append({"bestand": b64})

    MORCoreService().signaal_aanmaken(
        data=post_data,
    )
    del request.session["msb_melding"]
    return render(
        request,
        "msb/melding_importeren.html",
        {
            "msb_id": msb_id,
        },
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
            "melding/part_locatie_aanpassen.html",
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
