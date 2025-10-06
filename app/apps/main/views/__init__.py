import logging
import math
import os
from datetime import datetime

import requests
import weasyprint
from apps.context.constanten import FilterManager
from apps.context.utils import get_gebruiker_context
from apps.instellingen.models import Instelling
from apps.main.messages import MELDING_LIJST_OPHALEN_ERROR, MELDING_OPHALEN_ERROR
from apps.main.services import MORCoreService, TaakRService
from apps.main.templatetags.gebruikers_tags import get_gebruiker_object_middels_email
from apps.main.utils import (
    get_actieve_filters,
    get_ui_instellingen,
    update_qd_met_standaard_meldingen_filter_qd,
)
from apps.main.views.melding_detail import LogboekView  # NOQA
from apps.main.views.melding_detail import MeldingAfhandelenView  # NOQA
from apps.main.views.melding_detail import MeldingDetail  # NOQA
from apps.main.views.melding_detail import TakenAanmakenStreamView  # NOQA
from apps.main.views.melding_detail import TakenAanmakenView  # NOQA
from apps.main.views.melding_detail import informatie_toevoegen  # NOQA
from apps.main.views.melding_detail import locatie_aanpassen  # NOQA
from apps.main.views.melding_detail import melding_aanmaken  # NOQA
from apps.main.views.melding_detail import melding_annuleren  # NOQA
from apps.main.views.melding_detail import melding_heropenen  # NOQA
from apps.main.views.melding_detail import melding_hervatten  # NOQA
from apps.main.views.melding_detail import melding_locaties  # NOQA
from apps.main.views.melding_detail import melding_pauzeren  # NOQA
from apps.main.views.melding_detail import melding_spoed_veranderen  # NOQA
from apps.main.views.melding_detail import melding_taken  # NOQA
from apps.main.views.melding_detail import melding_verzonden  # NOQA
from apps.main.views.melding_detail import publiceer_topic  # NOQA
from apps.main.views.melding_detail import taak_verwijderen  # NOQA
from apps.main.views.melding_list import melding_lijst  # NOQA
from bs4 import BeautifulSoup
from config.context_processors import general_settings
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404, HttpResponse, QueryDict, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import TemplateView, View
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


class LichtmastView(PermissionRequiredMixin, TemplateView):
    template_name = "locatie/lichtmast.html"
    permission_required = "authorisatie.melding_bekijken"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lichtmast_id = self.kwargs.get("lichtmast_id")
        url = f"https://ows.gis.rotterdam.nl/cgi-bin/mapserv.exe?map=d:%5Cgwr%5Cwebdata%5Cmapserver%5Cmap%5Cbbdwh_pub.map&service=wfs&version=2.0.0&request=GetFeature&typeNames=namespace:sdo_gwr_bsb_ovl&Filter=<Filter><PropertyIsEqualTo><PropertyName>LICHTPUNT_ID</PropertyName><Literal>{lichtmast_id}</Literal></PropertyIsEqualTo></Filter>"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "xml")
        lichtmast_data = {}

        fields = (
            ("ms:MAST_ID", "Mast id", "mast_id"),
            ("ms:LICHTPUNT_ID", "Lichtpunt id", "lichtpunt_id"),
            ("ms:LICHTPUNTNUMMER", "Lichtpuntnummer", "lichtpuntnummer"),
            ("ms:LAMP_ID", "Lamp id", "lamp_id"),
            ("ms:STRAAT", "Straat", "straat"),
            ("ms:BEHEERDER", "Beheerder", "beheerder"),
            ("ms:EIGENAAR", "Eigenaar", "eigenaar"),
            ("ms:AMBITIENIVEAU", "Ambitieniveau", "ambitieniveau"),
            (
                "ms:LAATSTE_MUTATIE_ARMATUUR",
                "Laatste mutatie armatuur",
                "laatste_mutatie_armatuur",
            ),
            (
                "ms:LAATSTE_MUTATIE_LICHTBRON",
                "Laatste mutatie lichtbron",
                "laatste_mutatie_lichtbron",
            ),
            (
                "ms:PLAATSINGSDATUM_LICHTBRON",
                "Plaatsingsdatum lichtbron",
                "plaatsingsdatum_lichtbron",
            ),
            ("ms:IND_IN_STORING", "Storing", "storing"),
            (
                "ms:STORING_OMSCHRIJVINGEN",
                "Storings omschrijving",
                "storings_omschrijving",
            ),
            ("gml:pos", "rd", "rd"),
        )
        lichtmast_data = [
            (f[2], f[1], soup.find_all(f[0])[0].text if soup.find_all(f[0]) else "-")
            for f in fields
        ]
        if not [lm for lm in lichtmast_data if lm[2] != "-"]:
            return context
        rd_list = (
            lichtmast_data[-1][2].split(" ")
            if len(lichtmast_data[-1][2].split(" ")) == 2
            else []
        )
        rd = [float(xy) for xy in rd_list]
        lichtmast_data.append(("gps", "gps", rd_to_wgs(*rd) if rd else []))
        lichtmast_data = {
            lm[0]: {"value": lm[2], "label": lm[1]} for lm in lichtmast_data
        }
        context.update(
            {
                "lichtmast_data": lichtmast_data,
            }
        )
        return context


@login_required
@permission_required("authorisatie.medewerker_gegevens_bekijken", raise_exception=True)
def gebruiker_info(request, gebruiker_email):
    gebruiker = get_gebruiker_object_middels_email(gebruiker_email)
    return render(
        request,
        "melding/gebruiker_info.html",
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
            query_string=FilterManager(
                gebruiker_context=gebruiker_context
            ).get_query_string(meldingen_filter_query_dict)
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


class TaakRTaaktypeView(TemplateView):
    template_name = "taaktype/taakr.html"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        taakapplicatie_taaktype_url = self.request.GET.get(
            "taakapplicatie-taaktype-url"
        )
        if not taakapplicatie_taaktype_url:
            raise Http404

        taakr_taaktypes = TaakRService().get_taaktypes(
            params={
                "taakapplicatie_taaktype_url": taakapplicatie_taaktype_url,
            }
        )
        if not taakr_taaktypes:
            raise Http404

        afdelingen = TaakRService().get_afdelingen()
        afdelingen_middels_url = {
            afdeling["_links"]["self"]: afdeling["naam"] for afdeling in afdelingen
        }
        instelling = Instelling.actieve_instelling()
        if taakr_taaktypes:
            taaktype = taakr_taaktypes[0]
            voorbeeldsituaties = {
                "waarom_wel": [],
                "waarom_niet": [],
            }
            for voorbeeldsituatie_url in taaktype.get(
                "voorbeeldsituatie_voor_taaktype", []
            ):
                voorbeeldsituatie = TaakRService().haal_data(voorbeeldsituatie_url)
                voorbeeldsituaties[voorbeeldsituatie.get("type")].append(
                    voorbeeldsituatie
                )
            taaktype.update(voorbeeldsituaties)
            taaktype.update(
                {
                    "taakr_url": f"{instelling.taakr_basis_url}?taaktype_url={taakapplicatie_taaktype_url}",
                    "verantwoordelijke_afdeling": afdelingen_middels_url[
                        taaktype["verantwoordelijke_afdeling"]
                    ]
                    if taaktype.get("verantwoordelijke_afdeling")
                    else "",
                }
            )

            context.update({"taaktype": taaktype})
        return context
