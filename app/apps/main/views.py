import base64
import logging
import math

import requests
import weasyprint
from apps.authorisatie.models import (
    StandaardExterneOmschrijvingAanmakenPermissie,
    StandaardExterneOmschrijvingAanpassenPermissie,
    StandaardExterneOmschrijvingLijstBekijkenPermissie,
    StandaardExterneOmschrijvingVerwijderenPermissie,
)
from apps.context.constanten import FILTER_KEYS, FILTER_NAMEN, KOLOMMEN, KOLOMMEN_KEYS
from apps.context.utils import get_gebruiker_context
from apps.main.constanten import MSB_WIJKEN
from apps.main.forms import (
    TAAK_RESOLUTIE_GEANNULEERD,
    TAAK_STATUS_VOLTOOID,
    FilterForm,
    InformatieToevoegenForm,
    LocatieAanpassenForm,
    MeldingAanmakenForm,
    MeldingAfhandelenForm,
    MSBLoginForm,
    MSBMeldingZoekenForm,
    StandaardExterneOmschrijvingAanmakenForm,
    StandaardExterneOmschrijvingAanpassenForm,
    StandaardExterneOmschrijvingSearchForm,
    TaakAfrondenForm,
    TaakAnnulerenForm,
    TaakStartenForm,
)
from apps.main.models import StandaardExterneOmschrijving
from apps.main.utils import (
    get_open_taakopdrachten,
    melding_naar_tijdlijn,
    to_base64,
    update_qd_met_standaard_meldingen_filter_qd,
)
from apps.services.meldingen import MeldingenService, get_taaktypes
from config.context_processors import general_settings
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.files.storage import default_storage
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, QueryDict, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, View
from utils.rd_convert import rd_to_wgs

logger = logging.getLogger(__name__)


def http_404(request):
    return render(
        request,
        "404.html",
    )


def http_500(request):
    return render(
        request,
        "500.html",
    )


def root(request):
    if request.user.has_perms(["authorisatie.melding_lijst_bekijken"]):
        return redirect(reverse("melding_lijst"))
    if request.user.has_perms(["authorisatie.beheer_bekijken"]):
        return redirect(reverse("beheer"))
    return redirect(reverse("account"))


@login_required
def account(request):
    return render(
        request,
        "auth/account.html",
        {},
    )


@permission_required("authorisatie.melding_lijst_bekijken")
def melding_lijst(request):
    gebruiker_context = get_gebruiker_context(request)
    standaard_waardes = {
        "ordering": "-origineel_aangemaakt",
        "offset": "0",
    }

    query_dict = QueryDict("", mutable=True)
    query_dict.update(standaard_waardes)
    query_dict.update(request.GET)
    filter_query_dict = query_dict.copy()
    filter_query_dict.pop("offset")
    query_dict.update(
        {
            "limit": "10",
        }
    )
    for k in query_dict.keys():
        query_dict.setlist(k, list(dict.fromkeys(query_dict.getlist(k))))

    print("filter_query_dict")
    print(filter_query_dict.urlencode())
    print(request.session.get("overview_filter_querystring"))
    if (
        request.session.get("overview_filter_querystring")
        != filter_query_dict.urlencode()
    ):
        query_dict["offset"] = "0"
    request.session["overview_filter_querystring"] = filter_query_dict.urlencode()

    actieve_filters = FILTER_NAMEN
    kolommen = KOLOMMEN
    if gebruiker_context:
        actieve_filters = gebruiker_context.filters.get("fields", [])

        kolommen = [
            KOLOMMEN_KEYS.get(k)
            for k in gebruiker_context.kolommen.get("sorted", [])
            if KOLOMMEN_KEYS.get(k)
        ]
    actieve_filters = [f for f in actieve_filters if f in FILTER_NAMEN]

    meldingen_filter_query_dict = update_qd_met_standaard_meldingen_filter_qd(
        query_dict, gebruiker_context
    )
    data = MeldingenService().get_melding_lijst(
        query_string=meldingen_filter_query_dict.urlencode()
    )
    query_dict["limit"] = data.get("limit", 10)
    query_dict["offset"] = data.get("offset", 0)

    limit = data.get("limit", 10)

    pagina_aantal = math.ceil(data.get("count", 0) / limit)
    offset_options = [(str(p * limit), str(p + 1)) for p in range(0, pagina_aantal)]

    filter_velden = [
        {
            "naam": f,
            "opties": FILTER_KEYS[f](
                data.get("filter_options", {}).get(f, {})
            ).opties(),
            "aantal_actief": len(query_dict.getlist(f)),
        }
        for f in actieve_filters
    ]

    form = FilterForm(
        query_dict,
        filter_velden=filter_velden,
        offset_options=offset_options,
        gebruiker_context=gebruiker_context,
    )

    form.is_valid()
    if form.errors:
        logger.warning(form.errors)
    return render(
        request,
        "melding/melding_lijst.html",
        {
            "data": data,
            "form": form,
            "filter_options": data.get("filter_options", {}),
            "kolommen": kolommen,
        },
    )


@permission_required("authorisatie.melding_bekijken")
def melding_detail(request, id):
    melding = MeldingenService().get_melding(id)
    open_taakopdrachten = get_open_taakopdrachten(melding)
    tijdlijn_data = melding_naar_tijdlijn(melding)
    taaktypes = get_taaktypes(melding)
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
    form = InformatieToevoegenForm()
    overview_querystring = request.session.get("overview_querystring", "")
    if request.POST:
        form = InformatieToevoegenForm(request.POST)
        if form.is_valid():
            bijlagen = request.FILES.getlist("bijlagen", [])
            bijlagen_base64 = []
            for f in bijlagen:
                file_name = default_storage.save(f.name, f)
                bijlagen_base64.append({"bestand": to_base64(file_name)})

            MeldingenService().melding_status_aanpassen(
                id,
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                bijlagen=bijlagen_base64,
                gebruiker=request.user.email,
            )
            return redirect("melding_detail", id=id)
    aantal_actieve_taken = len(
        [
            to
            for to in melding.get("taakopdrachten_voor_melding", [])
            if to.get("status", {}).get("naam") != "voltooid"
        ]
    )

    aantal_voltooide_taken = len(
        [
            to
            for to in melding.get("taakopdrachten_voor_melding", [])
            if to.get("status", {}).get("naam") == "voltooid"
        ]
    )

    return render(
        request,
        "melding/melding_detail.html",
        {
            "melding": melding,
            "form": form,
            "overview_querystring": overview_querystring,
            "bijlagen_extra": bijlagen_flat,
            "taaktypes": taaktypes,
            "aantal_actieve_taken": aantal_actieve_taken,
            "aantal_voltooide_taken": aantal_voltooide_taken,
            "tijdlijn_data": tijdlijn_data,
            "open_taakopdrachten": open_taakopdrachten,
        },
    )


@permission_required("authorisatie.melding_afhandelen")
def melding_afhandelen(request, id):
    melding = MeldingenService().get_melding(id)
    afhandel_reden_opties = [(s, s) for s in melding.get("volgende_statussen", ())]
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
    form = MeldingAfhandelenForm()
    if request.POST:
        form = MeldingAfhandelenForm(request.POST)
        if form.is_valid():
            bijlagen = request.FILES.getlist("bijlagen", [])
            bijlagen_base64 = []
            for f in bijlagen:
                file_name = default_storage.save(f.name, f)
                bijlagen_base64.append({"bestand": to_base64(file_name)})

            MeldingenService().melding_status_aanpassen(
                id,
                omschrijving_extern=form.cleaned_data.get("omschrijving_extern"),
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                bijlagen=bijlagen_base64,
                gebruiker=request.user.email,
                status="afgehandeld",
                resolutie="opgelost",
            )
            return redirect("melding_detail", id=id)

    actieve_taken = [
        to
        for to in melding.get("taakopdrachten_voor_melding", [])
        if to.get("status", {}).get("naam") != "voltooid"
    ]

    return render(
        request,
        "melding/part_melding_afhandelen.html",
        {
            "form": form,
            "melding": melding,
            "afhandel_reden_opties": afhandel_reden_opties,
            "bijlagen": bijlagen_flat,
            "actieve_taken": actieve_taken,
            "aantal_actieve_taken": len(actieve_taken),
        },
    )


@permission_required("authorisatie.melding_annuleren")
def melding_annuleren(request, id):
    melding = MeldingenService().get_melding(id)
    afhandel_reden_opties = [(s, s) for s in melding.get("volgende_statussen", ())]
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
    form = MeldingAfhandelenForm()
    if request.POST:
        form = MeldingAfhandelenForm(request.POST)
        if form.is_valid():
            bijlagen = request.FILES.getlist("bijlagen", [])
            bijlagen_base64 = []
            for f in bijlagen:
                file_name = default_storage.save(f.name, f)
                bijlagen_base64.append({"bestand": to_base64(file_name)})

            MeldingenService().melding_annuleren(
                id,
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                bijlagen=bijlagen_base64,
                gebruiker=request.user.email,
            )
            return redirect("melding_detail", id=id)

    actieve_taken = [
        to
        for to in melding.get("taakopdrachten_voor_melding", [])
        if to.get("status", {}).get("naam") != "voltooid"
    ]

    return render(
        request,
        "melding/part_melding_annuleren.html",
        {
            "form": form,
            "melding": melding,
            "afhandel_reden_opties": afhandel_reden_opties,
            "bijlagen": bijlagen_flat,
            "actieve_taken": actieve_taken,
            "aantal_actieve_taken": len(actieve_taken),
        },
    )


@permission_required("authorisatie.taak_aanmaken")
def taak_starten(request, id):
    melding = MeldingenService().get_melding(id)
    taaktypes = get_taaktypes(melding)
    form = TaakStartenForm(taaktypes=taaktypes)
    if request.POST:
        form = TaakStartenForm(request.POST, taaktypes=taaktypes)
        if form.is_valid():
            data = form.cleaned_data
            taaktypes_dict = {tt[0]: tt[1] for tt in taaktypes}
            MeldingenService().taak_aanmaken(
                melding_uuid=id,
                taaktype_url=data.get("taaktype"),
                titel=taaktypes_dict.get(data.get("taaktype"), data.get("taaktype")),
                bericht=data.get("bericht"),
                gebruiker=request.user.email,
            )
            return redirect("melding_detail", id=id)

    return render(
        request,
        "melding/part_taak_starten.html",
        {
            "form": form,
            "melding": melding,
        },
    )


@permission_required("authorisatie.taak_afronden")
def taak_afronden(request, melding_uuid):
    melding = MeldingenService().get_melding(melding_uuid)
    open_taakopdrachten = get_open_taakopdrachten(melding)
    taakopdracht_urls = {
        to.get("uuid"): to.get("_links", {}).get("self") for to in open_taakopdrachten
    }
    taakopdracht_opties = [
        (to.get("uuid"), to.get("titel")) for to in open_taakopdrachten
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
            MeldingenService().taak_status_aanpassen(
                taakopdracht_url=taakopdracht_urls.get(
                    form.cleaned_data.get("taakopdracht")
                ),
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                bijlagen=bijlagen_base64,
                gebruiker=request.user.email,
                status=TAAK_STATUS_VOLTOOID,
                resolutie=form.cleaned_data.get("resolutie"),
            )

            return redirect("melding_detail", id=melding_uuid)

    return render(
        request,
        "melding/part_taak_afronden.html",
        {
            "form": form,
            "melding": melding,
        },
    )


@permission_required("authorisatie.taak_annuleren")
def taak_annuleren(request, melding_uuid):
    melding = MeldingenService().get_melding(melding_uuid)
    open_taakopdrachten = get_open_taakopdrachten(melding)
    taakopdracht_urls = {
        to.get("uuid"): to.get("_links", {}).get("self") for to in open_taakopdrachten
    }
    taakopdracht_opties = [
        (to.get("uuid"), to.get("titel")) for to in open_taakopdrachten
    ]
    form = TaakAnnulerenForm(taakopdracht_opties=taakopdracht_opties)
    if request.POST:
        form = TaakAnnulerenForm(request.POST, taakopdracht_opties=taakopdracht_opties)
        if form.is_valid():
            MeldingenService().taak_status_aanpassen(
                taakopdracht_url=taakopdracht_urls.get(
                    form.cleaned_data.get("taakopdracht")
                ),
                status=TAAK_STATUS_VOLTOOID,
                resolutie=TAAK_RESOLUTIE_GEANNULEERD,
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                gebruiker=request.user.email,
                bijlagen=[],
            )

            return redirect("melding_detail", id=melding_uuid)
    return render(
        request,
        "melding/part_taak_annuleren.html",
        {
            "form": form,
            "melding": melding,
        },
    )


@permission_required("authorisatie.melding_bekijken")
def informatie_toevoegen(request, id):
    melding = MeldingenService().get_melding(id)
    tijdlijn_data = melding_naar_tijdlijn(melding)
    form = InformatieToevoegenForm()
    if request.POST:
        form = InformatieToevoegenForm(request.POST)
        if form.is_valid():
            bijlagen = request.FILES.getlist("bijlagen_extra", [])
            bijlagen_base64 = []
            for f in bijlagen:
                file_name = default_storage.save(f.name, f)
                bijlagen_base64.append({"bestand": to_base64(file_name)})

            MeldingenService().melding_gebeurtenis_toevoegen(
                id,
                bijlagen=bijlagen_base64,
                omschrijving_intern=form.cleaned_data.get("opmerking"),
                gebruiker=request.user.email,
            )
            return redirect("melding_detail", id=id)

    return render(
        request,
        "melding/part_informatie_toevoegen.html",
        {
            "melding": melding,
            "form": form,
            "tijdlijn_data": tijdlijn_data,
        },
    )


@permission_required("authorisatie.melding_bekijken")
def melding_pdf_download(request, id):
    melding = MeldingenService().get_melding(id)
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


def meldingen_bestand(request):
    url = f"{settings.MELDINGEN_URL}{request.path}"
    headers = {"Authorization": f"Token {MeldingenService().haal_token()}"}
    response = requests.get(url, stream=True, headers=headers)
    return StreamingHttpResponse(
        response.raw,
        content_type=response.headers.get("content-type"),
        status=response.status_code,
        reason=response.reason,
    )


@permission_required("authorisatie.melding_aanmaken")
def melding_aanmaken(request):
    if request.POST:
        form = MeldingAanmakenForm(request.POST, request.FILES)
        bijlagen = request.FILES.getlist("bijlagen", [])
        file_names = []
        for f in bijlagen:
            file_name = default_storage.save(f.name, f)
            file_names.append(file_name)
        is_valid = form.is_valid()
        if is_valid:
            signaal_data = form.signaal_data(file_names)
            logger.info(signaal_data)
            signaal_response = MeldingenService().signaal_aanmaken(
                data=signaal_data,
            )
            logger.info(signaal_response)
            return redirect(
                reverse(
                    "melding_verzonden",
                    kwargs={"signaal_uuid": signaal_response.get("uuid")},
                )
            )
    else:
        form = MeldingAanmakenForm()

    return render(
        request,
        "melding/aanmaken.html",
        {
            "form": form,
        },
    )


@login_required
def melding_verzonden(request, signaal_uuid):
    return render(
        request,
        "melding/verzonden.html",
    )


@permission_required("authorisatie.msb_toegang")
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
            logger.info("msb_login=%s", response.status_code)
            if response.status_code == 200:
                request.session["msb_token"] = response.json().get("result")
                request.session["msb_base_url"] = msb_base_url
                return redirect(reverse("msb_melding_zoeken"))
            logger.error("msb_login error=%s", response.text)
            errors = [response.text]

    return render(request, "msb/login.html", {"form": form, "errors": errors})


@permission_required("authorisatie.msb_toegang")
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
            logger.info("msb melding url=%s", url)
            response = requests.get(
                url,
                headers={
                    "Authorization": f"Bearer {request.session.get('msb_token')}",
                },
            )
            logger.info(
                "msb melding zoeken response.status_code=%s",
                response.status_code,
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


@permission_required("authorisatie.msb_toegang")
def msb_importeer_melding(request):
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
            "buurtnaam": b.get("omschrijving"),
            "wijknaam": w.get("omschrijving"),
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

    omschrijving_kort = (
        msb_data.get("omschrijving", "")
        if msb_data.get("omschrijving")
        else "- geen korte omschrijving beschikbaar -"
    )

    post_data = {
        "signaal_url": "https://planr.rotterdam.nl/melding/signaal/42",
        "melder": {
            "naam": msb_data.get("melder", {}).get("naam"),
            "email": msb_data.get("melder", {}).get("email"),
            "telefoonnummer": msb_data.get("melder", {}).get("telefoon"),
        },
        "origineel_aangemaakt": msb_data.get("datumMelding", now.isoformat()),
        "onderwerpen": [
            f"{settings.MELDINGEN_URL}/api/v1/onderwerp/grofvuil-op-straat/"
        ],
        "omschrijving_kort": omschrijving_kort[:500],
        "omschrijving": msb_data.get("aanvullendeInformatie", ""),
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
        post_data["adressen"][0]["buurtnaam"] = wijk_buurt[0].get("buurtnaam")
        post_data["adressen"][0]["wijknaam"] = wijk_buurt[0].get("wijknaam")
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

    logger.info("signaal aanmaken data=%s", post_data)
    foto_urls = [f"{msb_base_url}{f.get('url')}" for f in msb_data.get("fotos", [])]
    logger.info("msb foto urls=%s", foto_urls)

    post_data["bijlagen"] = []
    for f in foto_urls:
        f_response = requests.get(
            url=f,
            headers={
                "Authorization": f"Bearer {request.session.get('msb_token')}",
            },
            stream=True,
        )
        logger.info("foto_response.status_code=%s", f_response.status_code)
        b64 = _to_base64(f_response.content)
        post_data["bijlagen"].append({"bestand": b64})

    signaal_response = MeldingenService().signaal_aanmaken(
        data=post_data,
    )
    logger.info("signaal aanmaken response=%s", signaal_response)
    del request.session["msb_melding"]
    return render(
        request,
        "msb/melding_importeren.html",
        {
            "msb_id": msb_id,
        },
    )


# Standaard externe omschrijving views
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
    StandaardExterneOmschrijvingView, PermissionRequiredMixin, CreateView
):
    form_class = StandaardExterneOmschrijvingAanmakenForm
    template_name = (
        "standaard_externe_omschrijving/standaard_externe_omschrijving_aanmaken.html"
    )
    permission_required = "authorisatie.standaard_externe_omschrijving_aanmaken"


class StandaardExterneOmschrijvingAanpassenView(
    StandaardExterneOmschrijvingView, PermissionRequiredMixin, UpdateView
):
    form_class = StandaardExterneOmschrijvingAanpassenForm
    template_name = (
        "standaard_externe_omschrijving/standaard_externe_omschrijving_aanpassen.html"
    )
    permission_required = "authorisatie.standaard_externe_omschrijving_aanpassen"


class StandaardExterneOmschrijvingVerwijderenView(
    StandaardExterneOmschrijvingView, PermissionRequiredMixin, DeleteView
):
    permission_required = "authorisatie.standaard_externe_omschrijving_verwijderen"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


# Locatie views


@permission_required("authorisatie.locatie_aanpassen")
def locatie_aanpassen(request, id):
    try:
        melding = MeldingenService().get_melding(id)
        afhandel_reden_opties = [(s, s) for s in melding.get("volgende_statussen", ())]

        locaties_voor_melding = melding.get("locaties_voor_melding", [])

        highest_gewicht_locatie = max(
            locaties_voor_melding, key=lambda locatie: locatie.get("gewicht", 0)
        )

        form_initial = {
            "geometrie": highest_gewicht_locatie.get("geometrie", "")
            if highest_gewicht_locatie
            else "",
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
                    "buurtnaam": form.cleaned_data.get("buurtnaam"),
                    "wijknaam": form.cleaned_data.get("wijknaam"),
                    "plaatsnaam": form.cleaned_data.get("plaatsnaam"),
                }

                MeldingenService().locatie_aanpassen(
                    id,
                    omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                    locatie=locatie_data,
                    gebruiker=request.user.email,
                )
                return redirect("melding_detail", id=id)

        actieve_taken = [
            to
            for to in melding.get("taakopdrachten_voor_melding", [])
            if to.get("status", {}).get("naam") != "voltooid"
        ]

        return render(
            request,
            "melding/part_locatie_aanpassen.html",
            {
                "form": form,
                "melding": melding,
                "afhandel_reden_opties": afhandel_reden_opties,
                "actieve_taken": actieve_taken,
                "aantal_actieve_taken": len(actieve_taken),
            },
        )
    except MeldingenService.AntwoordFout as e:
        return JsonResponse(
            {"error": str(e)},
            status=getattr(e, "status_code", 500),
        )
