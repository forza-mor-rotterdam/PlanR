import base64
import logging
import math

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
    TaakStartenForm,
    TaaktypeCategorieAanmakenForm,
    TaaktypeCategorieAanpassenForm,
    TaaktypeCategorieSearchForm,
)
from apps.main.models import StandaardExterneOmschrijving, TaaktypeCategorie
from apps.main.templatetags.gebruikers_tags import get_gebruiker_object_middels_email
from apps.main.utils import (
    get_actieve_filters,
    get_open_taakopdrachten,
    get_ordering,
    get_valide_kolom_classes,
    melding_locaties,
    melding_naar_tijdlijn,
    publiceer_topic_met_subscriptions,
    set_actieve_filters,
    set_ordering,
    to_base64,
    update_qd_met_standaard_meldingen_filter_qd,
)
from apps.services.meldingen import MeldingenService
from apps.services.taakr import TaakRService
from config.context_processors import general_settings
from deepdiff import DeepDiff
from django.conf import settings
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
    user_passes_test,
)
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, QueryDict, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, View
from utils.diversen import get_index
from utils.rd_convert import rd_to_wgs

logger = logging.getLogger(__name__)


def http_403(request):
    return render(
        request,
        "403.html",
    )


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


@login_required
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
def melding_lijst(request):
    meldingen_service = MeldingenService(request=request)
    meldingen_service.set_gebruiker(
        gebruiker=request.user.serialized_instance(),
    )
    gebruiker = request.user
    gebruiker_context = get_gebruiker_context(gebruiker)

    standaard_waardes = {
        "limit": "10",
        "ordering": get_ordering(gebruiker),
        "foldout_states": "[]",
    }
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
        standaard_waardes["ordering"] = set_ordering(
            gebruiker, qs.get("ordering", standaard_waardes["ordering"])
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
        form_qs.update({"q": request.session.get("q")})
    form_qs.update(standaard_waardes)

    for k, v in actieve_filters.items():
        if v:
            form_qs.setlist(k, v)

    meldingen_filter_query_dict = update_qd_met_standaard_meldingen_filter_qd(
        form_qs, gebruiker_context
    )
    meldingen_data = meldingen_service.get_melding_lijst(
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
        meldingen_data = meldingen_service.get_melding_lijst(
            query_string=FilterManager().get_query_string(meldingen_filter_query_dict)
        )
    request.session["pagina_melding_ids"] = [
        r.get("uuid") for r in meldingen_data.get("results")
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
    meldingen_service = MeldingenService(request=request)
    melding = meldingen_service.get_melding(id)

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

    open_taakopdrachten = get_open_taakopdrachten(melding)
    tijdlijn_data = melding_naar_tijdlijn(melding)
    locaties = melding_locaties(melding)
    taaktypes = TaakRService(request=request).get_niet_actieve_taaktypes(melding)
    categorized_taaktypes = TaakRService(request=request).categorize_taaktypes(
        melding, taaktypes
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
    form = InformatieToevoegenForm()
    overview_querystring = request.session.get("overview_querystring", "")
    if request.method == "POST":
        form = InformatieToevoegenForm(request.POST, request.FILES)
        if form.is_valid():
            opmerking = form.cleaned_data.get("opmerking")
            bijlagen = request.FILES.getlist("bijlagen_extra")
            bijlagen_base64 = []
            for f in bijlagen:
                file_name = default_storage.save(f.name, f)
                bijlagen_base64.append({"bestand": to_base64(file_name)})

            meldingen_service.melding_gebeurtenis_toevoegen(
                id,
                bijlagen=bijlagen_base64,
                omschrijving_intern=opmerking,
                gebruiker=request.user.email,
            )
            return redirect("melding_detail", id=id)
    taakopdrachten_voor_melding = [
        taakopdracht for taakopdracht in melding.get("taakopdrachten_voor_melding", [])
    ]
    aantal_actieve_taken = len(
        [
            taakopdracht
            for taakopdracht in taakopdrachten_voor_melding
            if taakopdracht.get("status", {}).get("naam")
            not in {"voltooid", "voltooid_met_feedback"}
        ]
    )

    aantal_opgeloste_taken = len(
        [
            taakopdracht
            for taakopdracht in taakopdrachten_voor_melding
            if taakopdracht.get("resolutie") == "opgelost"
        ]
    )

    aantal_niet_opgeloste_taken = len(
        [
            taakopdracht
            for taakopdracht in taakopdrachten_voor_melding
            if taakopdracht.get("resolutie")
            in ("niet_opgelost", "geannuleerd", "niet_gevonden")
        ]
    )

    return render(
        request,
        "melding/melding_detail.html",
        {
            "melding": melding,
            "locaties": locaties,
            "form": form,
            "overview_querystring": overview_querystring,
            "bijlagen_extra": bijlagen_flat,
            "taaktypes": categorized_taaktypes,
            "aantal_actieve_taken": aantal_actieve_taken,
            "aantal_opgeloste_taken": aantal_opgeloste_taken,
            "aantal_niet_opgeloste_taken": aantal_niet_opgeloste_taken,
            "tijdlijn_data": tijdlijn_data,
            "open_taakopdrachten": open_taakopdrachten,
            "meldingen_index": meldingen_index,
        },
    )


@login_required
@permission_required("authorisatie.melding_bekijken", raise_exception=True)
def melding_next(request, id, richting):
    meldingen_service = MeldingenService(request=request)
    melding_id = str(id)
    frame_id = "melding_next_volgend" if richting > 0 else "melding_next_vorige"
    label = "Volgende" if richting > 0 else "Vorige"

    pagina_item_aantal = 10
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
            "ordering": get_ordering(gebruiker),
            "q": request.session.get("q", ""),
            "offset": str(
                (int(pagina / pagina_item_aantal) + richting) * pagina_item_aantal
            ),
        }

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
        meldingen_data = meldingen_service.get_melding_lijst(
            query_string=meldingen_filter_query_dict.urlencode()
        )

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
    meldingen_service = MeldingenService(request=request)
    melding = meldingen_service.get_melding(id)

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

            meldingen_service.melding_status_aanpassen(
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
        taakopdracht
        for taakopdracht in melding.get("taakopdrachten_voor_melding", [])
        if taakopdracht.get("status", {}).get("naam")
        not in {"voltooid", "voltooid_met_feedback"}
    ]

    return render(
        request,
        "melding/part_melding_afhandelen.html",
        {
            "form": form,
            "melding": melding,
            "bijlagen": bijlagen_flat,
            "actieve_taken": actieve_taken,
            "aantal_actieve_taken": len(actieve_taken),
        },
    )


@login_required
@permission_required("authorisatie.melding_annuleren", raise_exception=True)
def melding_annuleren(request, id):
    meldingen_service = MeldingenService(request=request)
    melding = meldingen_service.get_melding(id)

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

            meldingen_service.melding_annuleren(
                id,
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                bijlagen=bijlagen_base64,
                gebruiker=request.user.email,
            )
            return redirect("melding_detail", id=id)

    actieve_taken = [
        taakopdracht
        for taakopdracht in melding.get("taakopdrachten_voor_melding", [])
        if taakopdracht.get("status", {}).get("naam")
        not in {"voltooid", "voltooid_met_feedback"}
    ]

    return render(
        request,
        "melding/part_melding_annuleren.html",
        {
            "form": form,
            "melding": melding,
            "bijlagen": bijlagen_flat,
            "actieve_taken": actieve_taken,
            "aantal_actieve_taken": len(actieve_taken),
        },
    )


@login_required
@permission_required("authorisatie.melding_heropenen", raise_exception=True)
def melding_heropenen(request, id):
    meldingen_service = MeldingenService(request=request)
    melding = meldingen_service.get_melding(id)
    form = MeldingHeropenenForm()
    if request.POST:
        form = MeldingHeropenenForm(request.POST)
        if form.is_valid():
            meldingen_service.melding_heropenen(
                id,
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                gebruiker=request.user.email,
            )
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
    meldingen_service = MeldingenService(request=request)
    melding = meldingen_service.get_melding(id)
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
            meldingen_service.melding_status_aanpassen(
                id,
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                gebruiker=request.user.email,
                status=form.cleaned_data.get("status"),
            )
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
    meldingen_service = MeldingenService(request=request)
    melding = meldingen_service.get_melding(id)
    form = MeldingHervattenForm()

    if request.POST:
        form = MeldingHervattenForm(request.POST)
        if form.is_valid():
            meldingen_service.melding_status_aanpassen(
                id,
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                gebruiker=request.user.email,
                status="openstaand",
            )
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
    meldingen_service = MeldingenService(request=request)
    melding = meldingen_service.get_melding(id)
    form = MeldingSpoedForm(
        initial={"urgentie": 0.5 if melding.get("urgentie", 0.2) == 0.2 else 0.2}
    )

    if request.POST:
        form = MeldingSpoedForm(request.POST)
        if form.is_valid():
            meldingen_service.melding_spoed_aanpassen(
                id,
                urgentie=form.cleaned_data.get("urgentie"),
                omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                gebruiker=request.user.email,
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


@login_required
@permission_required("authorisatie.taak_aanmaken", raise_exception=True)
def taak_starten(request, id):
    meldingen_service = MeldingenService(request=request)
    melding = meldingen_service.get_melding(id)

    # Get taak types for the user
    taaktypes = TaakRService(request=request).get_niet_actieve_taaktypes(melding)
    taaktypes_categorized = TaakRService(request=request).categorize_taaktypes(
        melding, taaktypes
    )

    # Categorize task types
    taaktype_categories = {}
    for taaktype_url, taaktype_omschrijving in taaktypes_categorized:
        categories = TaaktypeCategorie.objects.filter(
            taaktypes__contains=[taaktype_url]
        )
        category_name = categories.first().naam if categories.exists() else "Overig"
        taaktype_categories.setdefault(category_name, []).append(
            (taaktype_url, taaktype_omschrijving)
        )

    # Prepare task type choices for form
    taaktype_choices = [
        (category_name, category_taaktypes)
        for category_name, category_taaktypes in taaktype_categories.items()
    ]
    taaktype_choices.insert(0, ("", "Selecteer een taak"))

    # Prepare category choices for form
    categorie_choices = [
        (category_name, category_name) for category_name in taaktype_categories.keys()
    ]
    categorie_choices.insert(0, ("", "--"))

    form = TaakStartenForm(taaktypes=taaktype_choices, categories=categorie_choices)
    if request.POST:
        form = TaakStartenForm(
            request.POST, taaktypes=taaktype_choices, categories=categorie_choices
        )
        if form.is_valid():
            data = form.cleaned_data
            taaktypes_dict = {tt[0]: tt[1] for tt in taaktypes_categorized}
            meldingen_service.taak_aanmaken(
                melding_uuid=id,
                taakapplicatie_taaktype_url=data.get("taaktype"),
                titel=taaktypes_dict.get(data.get("taaktype"), data.get("taaktype")),
                bericht=data.get("bericht"),
                gebruiker=request.user.email,
            )
            return redirect("melding_detail", id=id)
        print(form.errors)

    return render(
        request,
        "melding/part_taak_starten.html",
        {
            "form": form,
            "melding": melding,
            "taaktype_choices": taaktype_choices,
        },
    )


@login_required
@permission_required("authorisatie.taak_afronden", raise_exception=True)
def taak_afronden(request, melding_uuid):
    meldingen_service = MeldingenService(request=request)
    melding = meldingen_service.get_melding(melding_uuid)

    open_taakopdrachten = get_open_taakopdrachten(melding)
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
            meldingen_service.taak_status_aanpassen(
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


@login_required
@permission_required("authorisatie.taak_annuleren", raise_exception=True)
def taak_annuleren(request, melding_uuid):
    meldingen_service = MeldingenService(request=request)
    melding = meldingen_service.get_melding(melding_uuid)

    open_taakopdrachten = get_open_taakopdrachten(melding)
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
            meldingen_service.taak_status_aanpassen(
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


@login_required
@permission_required("authorisatie.melding_bekijken", raise_exception=True)
def informatie_toevoegen(request, id):
    meldingen_service = MeldingenService(request=request)
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

            meldingen_service.melding_gebeurtenis_toevoegen(
                id,
                bijlagen=bijlagen_base64,
                omschrijving_intern=opmerking,
                gebruiker=request.user.email,
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
@permission_required("authorisatie.melding_bekijken", raise_exception=True)
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
    meldingen_service = MeldingenService(request=request)
    melding = meldingen_service.get_melding(id)
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
    instelling = Instelling.actieve_instelling()
    if not instelling:
        raise Exception(
            "De MOR-Core url kan niet worden gevonden, Er zijn nog geen instellingen aangemaakt"
        )
    meldingen_service = MeldingenService(request=request)
    modified_path = request.path.replace(settings.MOR_CORE_URL_PREFIX, "")
    url = f"{instelling.mor_core_basis_url}{modified_path}"
    headers = {"Authorization": f"Token {meldingen_service.haal_token()}"}
    response = requests.get(url, stream=True, headers=headers)
    return StreamingHttpResponse(
        response.raw,
        content_type=response.headers.get("content-type"),
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
            signaal_response = MeldingenService().signaal_aanmaken(
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
    if not instelling:
        raise Exception(
            "De MOR-Core url kan niet worden gevonden, Er zijn nog geen instellingen aangemaakt"
        )
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

    MeldingenService().signaal_aanmaken(
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


@login_required
@permission_required("authorisatie.locatie_aanpassen", raise_exception=True)
def locatie_aanpassen(request, id):
    try:
        meldingen_service = MeldingenService(request=request)
        melding = meldingen_service.get_melding(id)

        locaties_voor_melding = melding.get("locaties_voor_melding", [])

        highest_gewicht_locatie = max(
            locaties_voor_melding, key=lambda locatie: locatie.get("gewicht", 0)
        )

        form_initial = {
            "geometrie": (
                highest_gewicht_locatie.get("geometrie", "")
                if highest_gewicht_locatie
                else ""
            ),
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

                meldingen_service.locatie_aanpassen(
                    id,
                    omschrijving_intern=form.cleaned_data.get("omschrijving_intern"),
                    locatie=locatie_data,
                    gebruiker=request.user.email,
                )
                return redirect("melding_detail", id=id)

        actieve_taken = [
            taakopdracht
            for taakopdracht in melding.get("taakopdrachten_voor_melding", [])
            if taakopdracht.get("status", {}).get("naam")
            not in {"voltooid", "voltooid_met_feedback"}
        ]

        return render(
            request,
            "melding/part_locatie_aanpassen.html",
            {
                "form": form,
                "melding": melding,
                "actieve_taken": actieve_taken,
                "aantal_actieve_taken": len(actieve_taken),
            },
        )
    except MeldingenService.AntwoordFout as e:
        return JsonResponse(
            {"error": str(e)},
            status=getattr(e, "status_code", 500),
        )


@login_required
@user_passes_test(lambda u: u.is_superuser)
def clear_melding_token_from_cache(request):
    cache.delete("meldingen_token")
    return HttpResponse("melding_token removed from cache")


# Taaktype categorie view
class TaaktypeCategorieView(View):
    model = TaaktypeCategorie
    success_url = reverse_lazy("taaktype_categorie_lijst")


class TaaktypeCategorieLijstView(
    TaaktypeCategorieView, PermissionRequiredMixin, ListView
):
    context_object_name = "Taaktype categorieën"
    permission_required = "authorisatie.taaktype_categorie_lijst_bekijken"
    form_class = TaaktypeCategorieSearchForm
    template_name = "taaktype_categorie/taaktype_categorie_lijst.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("search", "")
        if search:
            queryset = queryset.filter(Q(naam__icontains=search))
        return queryset


class TaaktypeCategorieAanmakenView(
    TaaktypeCategorieView, PermissionRequiredMixin, CreateView
):
    form_class = TaaktypeCategorieAanmakenForm
    template_name = "taaktype_categorie/taaktype_categorie_aanmaken.html"
    permission_required = "authorisatie.taaktype_categorie_aanmaken"


class TaaktypeCategorieAanpassenView(
    TaaktypeCategorieView, PermissionRequiredMixin, UpdateView
):
    form_class = TaaktypeCategorieAanpassenForm
    template_name = "taaktype_categorie/taaktype_categorie_aanpassen.html"
    permission_required = "authorisatie.taaktype_categorie_aanpassen"


class TaaktypeCategorieVerwijderenView(
    TaaktypeCategorieView, PermissionRequiredMixin, DeleteView
):
    permission_required = "authorisatie.taaktype_categorie_verwijderen"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
