import logging
from datetime import datetime, timedelta

import isoweek
from apps.dashboard.forms import DashboardForm
from apps.dashboard.tables import get_aantallen_tabs, get_status_veranderingen_tabs
from apps.services.meldingen import MeldingenService
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse

logger = logging.getLogger(__name__)


@login_required
def dashboard(request, jaar=None, week=None):
    vandaag = datetime.now().date()
    vandaag_week = f"{vandaag.isocalendar().week:02}"

    try:
        w = isoweek.Week(int(jaar), int(week))
    except Exception:
        return redirect(reverse("dashboard_week", args=[vandaag.year, vandaag_week]))
    maandag = datetime.strptime(f"{w.year}-{w.week}-1", "%Y-%W-%w").date()

    if maandag > vandaag:
        return redirect(reverse("dashboard_week", args=[vandaag.year, vandaag_week]))

    if w.year != int(jaar):
        return redirect(reverse("dashboard_week", args=[w.year, f"{w.week:02}"]))

    def get_week(_jaar, _week):
        _w = isoweek.Week(int(_jaar), int(_week))
        if isoweek.Week.thisweek() < _w:
            return
        return (
            reverse(
                "dashboard_week",
                args=[_w.year, f"{_w.week:02}"],
            ),
            _w.week,
        )

    vorige_volgende_week = [
        get_week(w.year, w.week - 1),
        get_week(w.year, w.week + 1),
    ]

    meldingen = []
    signalen = []
    veranderingen = []
    meldingen_service = MeldingenService()
    for weekdag in range(0, 7):
        dag = maandag + timedelta(days=weekdag)
        melding_aantallen = meldingen_service.melding_aantallen(datum=dag)
        signaal_aantallen = meldingen_service.signaal_aantallen(datum=dag)
        status_veranderingen = meldingen_service.status_veranderingen(datum=dag)
        meldingen.append(melding_aantallen)
        signalen.append(signaal_aantallen)
        veranderingen.append(status_veranderingen)

    aantallen_tabs = get_aantallen_tabs(meldingen, signalen, w)
    status_veranderingen_tabs = get_status_veranderingen_tabs(veranderingen, w)

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
            "vorige_volgende_week": vorige_volgende_week,
            "aantallen_tabs": aantallen_tabs,
            "status_veranderingen_tabs": status_veranderingen_tabs,
        },
    )
