import logging
from datetime import datetime, timedelta

from apps.dashboard.forms import DashboardForm
from apps.main.constanten import DAGEN_VAN_DE_WEEK_KORT, MAANDEN_KORT, PDOK_WIJKEN
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
from django.shortcuts import redirect, render
from django.urls import reverse

logger = logging.getLogger(__name__)


@login_required
def dashboard(request, jaar=None, week=None):
    vandaag = datetime.now().date()
    vandaag_week = f"{vandaag.isocalendar().week:02}"

    try:
        maandag = datetime.strptime(f"{jaar}-{week}-1", "%Y-%W-%w").date()
    except Exception:
        return redirect(reverse("dashboard_week", args=[vandaag.year, vandaag_week]))

    if maandag > vandaag:
        return redirect(reverse("dashboard_week", args=[vandaag.year, vandaag_week]))

    # redirect to correct week number, because zero is allowed as correct week number
    if maandag.isocalendar().week == 1 and int(week) == 0:
        return redirect(
            reverse(
                "dashboard_week",
                args=[maandag.year, f"{maandag.isocalendar().week:02}"],
            )
        )

    def maandag_van_de_week(_jaar, _week):
        _maandag = None
        if int(_week) == 0:
            return
        try:
            _maandag = datetime.strptime(f"{_jaar}-{_week}-1", "%Y-%W-%w").date()
        except Exception:
            return
        if _maandag > vandaag:
            return
        return (
            reverse(
                "dashboard_week",
                args=[_maandag.year, f"{_maandag.isocalendar().week:02}"],
            ),
            _maandag.isocalendar().week,
        )

    vorige_volgende_week = [
        maandag_van_de_week(jaar, maandag.isocalendar().week - 1),
        maandag_van_de_week(jaar, maandag.isocalendar().week + 1),
    ]

    meldingen = []
    signalen = []
    labels = []
    meldingen_service = MeldingenService()
    for weekdag in range(0, 7):
        dag = maandag + timedelta(days=weekdag)
        melding_aantallen = meldingen_service.melding_aantallen(datum=dag)
        signaal_aantallen = meldingen_service.signaal_aantallen(datum=dag)
        meldingen.append(melding_aantallen)
        signalen.append(signaal_aantallen)
        labels.append(
            f"{DAGEN_VAN_DE_WEEK_KORT[weekdag]} {dag.strftime('%-d')} {MAANDEN_KORT[dag.month-1]}"
        )
    wijken = [wijk.get("wijknaam") for wijk in PDOK_WIJKEN]
    wijken_noord = [
        wijk.get("wijknaam") for wijk in PDOK_WIJKEN if wijk.get("stadsdeel") == "Noord"
    ]
    wijken_zuid = [
        wijk.get("wijknaam") for wijk in PDOK_WIJKEN if wijk.get("stadsdeel") == "Zuid"
    ]

    tabs = [
        {
            "wijken": [],
            "wijk_not_in": True,
            "titel": "Heel Rotterdam",
        },
        {
            "wijken": wijken_noord,
            "wijk_not_in": False,
            "titel": "Rotterdam noord",
        },
        {
            "wijken": wijken_zuid,
            "wijk_not_in": False,
            "titel": "Rotterdam zuid",
        },
        {
            "wijken": wijken,
            "wijk_not_in": True,
            "titel": "Onbekend of buiten Rotterdam",
        },
    ]

    tabs = [
        {
            **tab,
            **{
                "datasets": [
                    {
                        "type": "line",
                        "label": "Aantal meldingen",
                        "bron": meldingen,
                    },
                    {
                        "type": "bar",
                        "label": "Aantal signalen",
                        "bron": signalen,
                    },
                ]
            },
        }
        for tab in tabs
    ]

    tabs = [
        {
            "titel": tab.get("titel"),
            "labels": labels,
            "datasets": [
                {
                    "type": dataset.get("type"),
                    "label": dataset.get("label"),
                    "barPercentage": "0.2",
                    "borderColor": "#00811F",
                    "fill": True,
                    "backgroundColor": "rgba(0,200,100,0.1)",
                    "data": [
                        sum(
                            [
                                d.get("count")
                                for d in dag
                                if bool(d.get("wijk") in tab.get("wijken"))
                                != bool(tab.get("wijk_not_in"))
                            ]
                        )
                        for dag in dataset.get("bron")
                    ],
                }
                for dataset in tab.get("datasets", [])
            ],
        }
        for tab in tabs
    ]
    tabs = [
        {
            **tab,
            **{
                "aantallen": [
                    sum(dataset.get("data", [])) for dataset in tab.get("datasets", [])
                ]
            },
        }
        for tab in tabs
    ]

    onderwerp_opties = list(
        set([d.get("onderwerp") for kolom in meldingen for d in kolom])
    )
    wijk_opties = list(set([d.get("wijk") for kolom in meldingen for d in kolom]))

    form = DashboardForm(request.GET, wijken=wijk_opties, onderwerpen=onderwerp_opties)
    if form.is_valid():
        print(form.cleaned_data)

    return render(
        request,
        "dashboard.html",
        {
            "form": form,
            "jaar": jaar,
            "week": int(week),
            "labels": labels,
            "vorige_volgende_week": vorige_volgende_week,
            "tabs": tabs,
        },
    )
