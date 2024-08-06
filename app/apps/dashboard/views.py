import logging
from datetime import datetime, timedelta

from apps.dashboard.forms import DashboardForm
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
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
    user_passes_test,
)
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

logger = logging.getLogger(__name__)


@login_required
def dashboard(request, jaar=None, week=None):
    print(jaar)
    print(week)
    now = datetime.now()

    if not jaar and not week:
        return redirect(
            reverse("dashboard_week", args=[now.year, now.isocalendar().week])
        )

    if jaar and int(jaar) <= now.year and not week:
        return redirect(reverse("dashboard_week", args=[now.year, "01"]))
    if jaar and int(jaar) <= now.year and week and int(week) in range(0, 53):
        week_dagen = [
            "maandag",
            "dinsdag",
            "woensdag",
            "donderdag",
            "vrijdag",
            "zaterdag",
            "zondag",
        ]
        data = []
        print(now.isocalendar().week)
        maandag = datetime.strptime(f"{jaar}-{week}-1", "%Y-%W-%w").date()
        meldingen_service = MeldingenService()
        onderwerpen = []
        for weekdag in range(0, 7):
            dag = maandag + timedelta(days=weekdag)
            print(dag)
            melding_aantallen = meldingen_service.melding_aantallen(datum=dag)
            print(melding_aantallen)
            data.append(melding_aantallen)

        onderwerp_opties = list(
            set([d.get("onderwerp") for kolom in data for d in kolom])
        )
        wijk_opties = list(set([d.get("wijk") for kolom in data for d in kolom]))

        form = DashboardForm(
            request.GET, wijken=wijk_opties, onderwerpen=onderwerp_opties
        )
        if form.is_valid():
            onderwerpen = form.cleaned_data.get("onderwerp")
            [form.cleaned_data.get("wijk")]
        print(form.errors)
        print(onderwerpen)

        tbody = [
            [
                sum([d.get("count") for d in kolom if d.get("onderwerp") == onderwerp])
                for onderwerp in onderwerpen
            ]
            for kolom in data
        ]
        print(tbody)
        max_value = sorted([vv for v in tbody for vv in v])[-1]
        print(max_value)
        tbody = [
            [
                {
                    "count": vv,
                    "percentage": float(vv / max_value) * 100,
                }
                for vv in v
            ]
            for v in tbody
        ]
        print(len(onderwerpen))
        print(len(data))
        print(tbody)

        return render(
            request,
            "dashboard.html",
            {
                "tabel": {
                    "thead": [
                        week_dagen,
                        [onderwerpen for dag in week_dagen],
                    ],
                    "tbody": tbody,
                },
                "form": form,
            },
        )
    raise Http404
