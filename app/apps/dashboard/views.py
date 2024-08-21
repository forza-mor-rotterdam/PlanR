import calendar
import logging
from datetime import datetime, timedelta

import isoweek
from apps.dashboard.forms import DashboardForm
from apps.dashboard.tables import (
    get_aantallen_tabs,
    get_afgehandeld_tabs,
    get_status_veranderingen_tabs,
)
from apps.main.constanten import DAGEN_VAN_DE_WEEK_KORT, MAANDEN, MAANDEN_KORT
from apps.services.meldingen import MeldingenService
from django.contrib.auth.decorators import login_required
from django.contrib.gis.db import models
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic.edit import FormView

logger = logging.getLogger(__name__)


class Dashboard(FormView):
    form_class = DashboardForm
    template_name = "afgehandeld/dashboard.html"
    periode = None
    title = None
    week = maand = jaar = None

    def dispatch(self, request, *args, **kwargs):
        jaar_param = kwargs.get("jaar")
        maand_param = kwargs.get("maand")
        week_param = kwargs.get("week")

        datetime.now().date()
        try:
            self.week = isoweek.Week(int(jaar_param), int(week_param))
        except Exception as e:
            print(f"Tried week, next try maand: {e}")
            try:
                self.maand = calendar.monthrange(int(jaar_param), int(maand_param))
            except Exception as e:
                print(f"Tried maand, next try jaar: {e}")
                try:
                    self.jaar = int(jaar_param)
                except Exception as e:
                    print(f"Tried jaar, next redirect to current week: {e}")
        self.title = self.get_title()
        return super().dispatch(request, *args, **kwargs)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.periode:
            self.periode = self.PeriodeOpties.WEEK

    class PeriodeOpties(models.TextChoices):
        WEEK = "week", "Week"
        MAAND = "maand", "Maand"
        JAAR = "jaar", "Jaar"

    def get_title(self):
        jaar_param = self.kwargs.get("jaar")
        maand_param = self.kwargs.get("maand")
        week_param = self.kwargs.get("week")

        if self.week and self.periode == self.PeriodeOpties.WEEK:
            return f"week {int(week_param)} {int(jaar_param)}"

        if self.maand and self.periode == self.PeriodeOpties.MAAND:
            return f"maand {MAANDEN[int(maand_param)-1]} {int(jaar_param)}"

        if self.jaar and self.PeriodeOpties.JAAR:
            return f"jaar {int(jaar_param)}"

        return ""

    def get_x_ticks(self):
        jaar_param = self.kwargs.get("jaar")
        maand_param = self.kwargs.get("maand")
        self.kwargs.get("week")

        if self.week and self.periode == self.PeriodeOpties.WEEK:
            maandag = datetime.strptime(
                f"{self.week.year}-{self.week.week}-1", "%Y-%W-%w"
            ).date()
            if self.week.year != int(jaar_param):
                return redirect(
                    reverse(
                        "dashboard_week", args=[self.week.year, f"{self.week.week:02}"]
                    )
                )

            dagen = (maandag + timedelta(days=weekdag) for weekdag in range(0, 7))
            return [
                {
                    "start_dt": dag,
                    "type": "dag",
                    "label": f"{DAGEN_VAN_DE_WEEK_KORT[dag.weekday()]} {dag.strftime('%-d')} {MAANDEN_KORT[dag.month-1]}",
                }
                for dag in dagen
            ]
        if self.maand and self.periode == self.PeriodeOpties.MAAND:
            eerste_dag_vd_maand = datetime(int(jaar_param), int(maand_param), 1)
            dagen = [
                eerste_dag_vd_maand + timedelta(days=dag_vd_maand)
                for dag_vd_maand in range(0, self.maand[1])
            ]
            ticks = [
                {
                    "start_dt": dag,
                    "type": "maand",
                    "label": f"{dag.strftime('%-d')} {MAANDEN_KORT[dag.month-1]}",
                }
                for dag in dagen
            ]
            return ticks

        if self.jaar and self.PeriodeOpties.JAAR:
            eerste_dag_vd_maand = datetime(int(jaar_param), int(maand_param), 1)
            dagen = [
                eerste_dag_vd_maand + timedelta(days=dag_vd_maand)
                for dag_vd_maand in range(0, self.maand[1])
            ]
            ticks = [
                {
                    "start_dt": dag,
                    "type": "maand",
                    "label": f"{dag.strftime('%-d')} {MAANDEN_KORT[dag.month-1]}",
                }
                for dag in dagen
            ]
            return ticks

        return []

    def get_week_links(self, _jaar, _week):
        _w = isoweek.Week(int(_jaar), int(_week))
        if isoweek.Week.thisweek() < _w:
            return
        return (
            reverse(
                "dashboard",
                kwargs={
                    "jaar": _w.year,
                    "week": f"{_w.week:02}",
                    "type": self.kwargs.get("type"),
                    "status": self.kwargs.get("status"),
                },
            ),
            f"week {_w.week}, {_w.year}",
        )

    def get_maand_links(self, jaar, maand):
        if maand == 0:
            jaar = jaar - 1
            maand = 12
        if maand == 13:
            jaar = jaar + 1
            maand = 1
        try:
            dt = datetime(year=jaar, month=maand, day=1)
        except Exception:
            return
        vandaag = datetime.now().date()
        if dt.year == vandaag.year and dt.month > vandaag.month:
            return
        return (
            reverse(
                "dashboard",
                kwargs={
                    "jaar": dt.year,
                    "maand": f"{dt.month:02}",
                    "type": self.kwargs.get("type"),
                    "status": self.kwargs.get("status"),
                },
            ),
            f"{MAANDEN[dt.month-1]} {dt.year}",
        )

    def get_periode_navigatie(self):
        self.kwargs.get("jaar")
        maand_param = self.kwargs.get("maand")
        week_param = self.kwargs.get("week")

        periodes = {
            str(self.PeriodeOpties.MAAND): maand_param,
            str(self.PeriodeOpties.WEEK): week_param,
        }
        extra_kwargs = {}
        if self.week and self.periode == self.PeriodeOpties.WEEK:
            extra_kwargs = {
                str(self.PeriodeOpties.MAAND): "01",
            }

        if self.maand and self.periode == self.PeriodeOpties.MAAND:
            extra_kwargs = {
                str(self.PeriodeOpties.WEEK): "01",
            }

        kwargs = {
            k: v
            for k, v in self.kwargs.items()
            if k not in [str(self.PeriodeOpties.MAAND), str(self.PeriodeOpties.WEEK)]
        }
        kwargs.update(extra_kwargs)
        periodes = [
            [
                reverse(
                    "dashboard",
                    kwargs=kwargs,
                )
                if not self.kwargs.get(k)
                else 0,
                k,
            ]
            for k, v in periodes.items()
        ]
        return periodes

    def get_periode_type_navigatie(self):
        jaar_param = self.kwargs.get("jaar")
        maand_param = self.kwargs.get("maand")
        self.kwargs.get("week")

        if self.week and self.periode == self.PeriodeOpties.WEEK:
            return [
                self.get_week_links(self.week.year, self.week.week - 1),
                [0, f"week {self.week.week}, {int(jaar_param)}"],
                self.get_week_links(self.week.year, self.week.week + 1),
            ]

        if self.maand and self.periode == self.PeriodeOpties.MAAND:
            return [
                self.get_maand_links(int(jaar_param), int(maand_param) - 1),
                [0, f"{MAANDEN[int(maand_param)-1]} {int(jaar_param)}"],
                self.get_maand_links(int(jaar_param), int(maand_param) + 1),
            ]
        if self.jaar and self.PeriodeOpties.JAAR:
            return []
        return []

    def get_status_navigatie(self):
        jaar_param = self.kwargs.get("jaar")
        maand_param = self.kwargs.get("maand")
        week_param = self.kwargs.get("week")

        periodes = {
            self.PeriodeOpties.MAAND: maand_param,
            self.PeriodeOpties.WEEK: week_param,
        }

        statussen = [
            [f"Nieuwe {self.kwargs.get('type')}", "nieuw"],
            [f"Afgehandelde {self.kwargs.get('type')}", "afgehandeld"],
        ]
        default_kwargs = {
            "jaar": jaar_param,
            f"{self.periode}": periodes[self.periode],
            "type": self.kwargs.get("type"),
        }

        statussen = [
            {
                "title": status[0],
                "status": status[1],
                "kwargs": {**default_kwargs, **{"status": status[1]}},
            }
            for status in statussen
        ]

        for status in statussen:
            y = self.kwargs
            x = status.get("kwargs")
            shared_items = {k: x[k] for k in x if k in y and x[k] != y[k]}
            if not shared_items:
                status["kwargs"] = {}

        return [
            [
                reverse(
                    "dashboard",
                    kwargs=status.get("kwargs"),
                )
                if status.get("kwargs")
                else 0,
                status.get("title"),
            ]
            for status in statussen
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.x_ticks = self.get_x_ticks()
        context["periode"] = self.periode
        context.update(
            {
                "periode_navigatie": self.get_periode_navigatie(),
                "periode_type_navigatie": self.get_periode_type_navigatie(),
                "status_navigatie": self.get_status_navigatie(),
                "title": self.title,
            }
        )
        context.update(self.kwargs)
        return context


class NieuweMeldingen(Dashboard):
    template_name = "dashboard/nieuwe/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        meldingen = []
        signalen = []
        veranderingen = []
        meldingen_service = MeldingenService()
        for tick in self.x_ticks:
            dag = tick.get("start_dt")
            melding_aantallen = meldingen_service.melding_aantallen(datum=dag)
            signaal_aantallen = meldingen_service.signaal_aantallen(datum=dag)
            status_veranderingen = meldingen_service.status_veranderingen(datum=dag)
            meldingen.append(melding_aantallen)
            signalen.append(signaal_aantallen)
            veranderingen.append(status_veranderingen)

        aantallen_tabs = get_aantallen_tabs(meldingen, signalen, ticks=self.x_ticks)
        status_veranderingen_tabs = get_status_veranderingen_tabs(
            veranderingen, ticks=self.x_ticks
        )

        context.update(
            {
                "aantallen_tabs": aantallen_tabs,
                "status_veranderingen_tabs": status_veranderingen_tabs,
            }
        )
        return context


class MeldingenAfgehandeld(Dashboard):
    template_name = "dashboard/afgehandeld/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        afgehandeld = []
        meldingen_service = MeldingenService()
        for tick in self.x_ticks:
            dag = tick.get("start_dt")
            status_afgehandeld = meldingen_service.afgehandelde_meldingen(datum=dag)
            afgehandeld.append(status_afgehandeld)

        afgehandeld_tabs = get_afgehandeld_tabs(afgehandeld, ticks=self.x_ticks)

        stacked_bars_options = {
            "plugins": {
                "legend": {
                    "display": True,
                },
                "tooltip": {
                    "backgroundColor": "#ffffff",
                    "borderColor": "rgba(0, 0 ,0 , .8)",
                    "borderWidth": 1,
                    "bodyAlign": "center",
                    "bodyColor": "#000000",
                    "titleColor": "#000000",
                    "titleAlign": "center",
                    "displayColors": False,
                    "borderRadius": 0,
                },
            },
            "scales": {
                "x": {"stacked": True},
                "y": {
                    "stacked": True,
                    "grid": {
                        "display": False,
                    },
                },
            },
        }

        context.update(
            {
                "afgehandeld_tabs": afgehandeld_tabs,
                "stacked_bars_options": stacked_bars_options,
            }
        )
        return context


@login_required
def dashboard(request, jaar_param=None, week=None):
    vandaag = datetime.now().date()
    vandaag_week = f"{vandaag.isocalendar().week:02}"

    try:
        w = isoweek.Week(int(jaar_param), int(week))
    except Exception:
        return redirect(reverse("dashboard_week", args=[vandaag.year, vandaag_week]))
    maandag = datetime.strptime(f"{w.year}-{w.week}-1", "%Y-%W-%w").date()

    if maandag > vandaag:
        return redirect(reverse("dashboard_week", args=[vandaag.year, vandaag_week]))

    if w.year != int(jaar_param):
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

    aantallen_tabs = get_aantallen_tabs(meldingen, signalen, week=w)
    status_veranderingen_tabs = get_status_veranderingen_tabs(veranderingen, week=w)

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
            "jaar_param": jaar_param,
            "week": int(week),
            "vorige_volgende_week": vorige_volgende_week,
            "aantallen_tabs": aantallen_tabs,
            "status_veranderingen_tabs": status_veranderingen_tabs,
        },
    )
