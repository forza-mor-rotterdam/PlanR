import calendar
import copy
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
from django.contrib.auth.decorators import permission_required
from django.contrib.gis.db import models
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

logger = logging.getLogger(__name__)


class Dashboard(FormView):
    form_class = DashboardForm
    template_name = "afgehandeld/dashboard.html"
    periode = None
    title = None
    week = maand = jaar = None

    # def form_valid(self, form):
    #     print("form.cleaned_data")
    #     print(form.cleaned_data)
    #     return super().form_valid(form)

    # def form_invalid(self,form):
    # # Add action to invalid form phase
    #     print(form.errors)
    #     return self.render_to_response(self.get_context_data(form=form))

    def dispatch(self, request, *args, **kwargs):
        jaar_param = kwargs.get("jaar")
        maand_param = kwargs.get("maand")
        week_param = kwargs.get("week")

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
                    vandaag = datetime.now().date()
                    return redirect(
                        reverse(
                            "dashboard",
                            kwargs={
                                "jaar": vandaag.year,
                                "week": f"{vandaag.isocalendar().week:02}",
                                "type": "meldingen",
                                "status": "nieuw",
                            },
                        )
                    )

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

            dagen = (maandag + timedelta(days=weekdag) for weekdag in range(0, 7))
            return [
                {
                    "start_dt": dag,
                    "type": "dag",
                    "days": 1,
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
                    "type": "dag",
                    "days": 1,
                    "label": f"{dag.strftime('%-d')} {MAANDEN_KORT[dag.month-1]}",
                }
                for dag in dagen
            ]
            return ticks

        if self.jaar and self.PeriodeOpties.JAAR:
            maanden = [
                datetime(int(jaar_param), maand + 1, 1) for maand in range(0, 12)
            ]
            print(maanden)
            ticks = [
                {
                    "start_dt": dag,
                    "type": "maand",
                    "days": calendar.monthrange(dag.year, dag.month)[1],
                    "label": f"{MAANDEN[dag.month-1]}",
                }
                for dag in maanden
            ]
            print(ticks)
            return ticks

        return []

    def get_week_links(self, _jaar, _week):
        _w = isoweek.Week(int(_jaar), int(_week))
        if isoweek.Week.thisweek() < _w:
            return
        return (
            f"week {_w.week}, {_w.year}",
            reverse(
                "dashboard",
                kwargs={
                    "jaar": _w.year,
                    "week": f"{_w.week:02}",
                    "type": self.kwargs.get("type"),
                    "status": self.kwargs.get("status"),
                },
            ),
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
            f"{MAANDEN[dt.month-1]} {dt.year}",
            reverse(
                "dashboard",
                kwargs={
                    "jaar": dt.year,
                    "maand": f"{dt.month:02}",
                    "type": self.kwargs.get("type"),
                    "status": self.kwargs.get("status"),
                },
            ),
        )

    def get_jaar_links(self, jaar):
        vandaag = datetime.now().date()
        if int(jaar) > vandaag.year:
            return ["", ""]
        return (
            jaar,
            reverse(
                "dashboard",
                kwargs={
                    "jaar": jaar,
                    "type": self.kwargs.get("type"),
                    "status": self.kwargs.get("status"),
                },
            ),
        )

    def get_periode_navigatie(self):
        self.kwargs.get("jaar")
        maand_param = self.kwargs.get("maand", "01")
        week_param = self.kwargs.get("week", "01")

        kwargs = {
            k: v
            for k, v in self.kwargs.items()
            if k not in [str(self.PeriodeOpties.MAAND), str(self.PeriodeOpties.WEEK)]
        }

        periodes = {
            str(self.PeriodeOpties.JAAR): copy.deepcopy(kwargs),
            str(self.PeriodeOpties.MAAND): {
                **copy.deepcopy(kwargs),
                **{str(self.PeriodeOpties.MAAND): maand_param},
            },
            str(self.PeriodeOpties.WEEK): {
                **copy.deepcopy(kwargs),
                **{str(self.PeriodeOpties.WEEK): week_param},
            },
        }
        periodes = {
            k: reverse(
                "dashboard",
                kwargs=v,
            )
            for k, v in periodes.items()
        }
        periodes[self.periode] = ""
        return [
            [str(self.PeriodeOpties.JAAR), periodes[str(self.PeriodeOpties.JAAR)]],
            [str(self.PeriodeOpties.MAAND), periodes[str(self.PeriodeOpties.MAAND)]],
            [str(self.PeriodeOpties.WEEK), periodes[str(self.PeriodeOpties.WEEK)]],
        ]

    def get_periode_type_navigatie(self):
        jaar_param = self.kwargs.get("jaar")
        maand_param = self.kwargs.get("maand")
        self.kwargs.get("week")

        if self.week and self.periode == self.PeriodeOpties.WEEK:
            return [
                self.get_week_links(self.week.year, self.week.week - 1),
                [f"week {self.week.week}, {int(jaar_param)}", 0],
                self.get_week_links(self.week.year, self.week.week + 1),
            ]

        if self.maand and self.periode == self.PeriodeOpties.MAAND:
            return [
                self.get_maand_links(int(jaar_param), int(maand_param) - 1),
                [f"{MAANDEN[int(maand_param)-1]} {int(jaar_param)}", 0],
                self.get_maand_links(int(jaar_param), int(maand_param) + 1),
            ]
        if self.jaar and self.PeriodeOpties.JAAR:
            return [
                self.get_jaar_links(int(jaar_param) - 1),
                [jaar_param, 0],
                self.get_jaar_links(int(jaar_param) + 1),
            ]
        return []

    def get_status_navigatie(self):
        statussen = {
            "nieuw": f"Nieuwe {self.kwargs.get('type')}",
            "afgehandeld": f"Afgehandelde {self.kwargs.get('type')}",
        }

        statussen = {
            k: [
                v,
                reverse(
                    "dashboard",
                    kwargs={
                        **copy.deepcopy(self.kwargs),
                        **{
                            "status": k,
                        },
                    },
                ),
            ]
            for k, v in statussen.items()
        }

        statussen[self.kwargs.get("status")] = [
            statussen[self.kwargs.get("status")][0],
            "",
        ]

        return [[v[0], v[1]] for k, v in statussen.items()]

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


@method_decorator(
    permission_required("authorisatie.dashboard_bekijken"), name="dispatch"
)
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
            days = tick.get("days")
            melding_aantallen = meldingen_service.melding_aantallen(
                datum=dag, days=days
            )
            signaal_aantallen = meldingen_service.signaal_aantallen(
                datum=dag, days=days
            )
            status_veranderingen = meldingen_service.status_veranderingen(
                datum=dag, days=days
            )
            meldingen.append(melding_aantallen)
            signalen.append(signaal_aantallen)
            veranderingen.append(status_veranderingen)

        aantallen_tabs = get_aantallen_tabs(meldingen, signalen, ticks=self.x_ticks)
        status_veranderingen_tabs = get_status_veranderingen_tabs(
            veranderingen, ticks=self.x_ticks
        )

        meldingen_aantal = sum(
            [sum([d.get("count") for d in kolom]) for kolom in meldingen]
        )
        print(meldingen_aantal)
        onderwerp_opties = list(
            set([d.get("onderwerp") for kolom in meldingen for d in kolom])
        )
        wijk_opties = list(set([d.get("wijk") for kolom in meldingen for d in kolom]))

        onderwerpen = [
            {
                "label": onderwerp,
                "aantal": sum(
                    [
                        d.get("count")
                        for kolom in meldingen
                        for d in kolom
                        if d.get("onderwerp") == onderwerp
                    ]
                ),
            }
            for onderwerp in onderwerp_opties
        ]
        wijken = [
            {
                "label": wijk,
                "aantal": sum(
                    [
                        d.get("count")
                        for kolom in meldingen
                        for d in kolom
                        if d.get("wijk") == wijk
                    ]
                ),
            }
            for wijk in wijk_opties
        ]
        onderwerpen = sorted(
            [
                {
                    **onderwerp,
                    **{
                        "percentage": int(
                            float(onderwerp.get("aantal") / meldingen_aantal) * 100
                        ),
                        "bar": int(
                            float(onderwerp.get("aantal") / meldingen_aantal) * 100
                        ),
                    },
                }
                for onderwerp in onderwerpen
            ],
            key=lambda b: b.get("percentage"),
            reverse=True,
        )
        wijken = sorted(
            [
                {
                    **wijk,
                    **{
                        "percentage": int(
                            float(wijk.get("aantal") / meldingen_aantal) * 100
                        ),
                        "bar": int(float(wijk.get("aantal") / meldingen_aantal) * 100),
                    },
                }
                for wijk in wijken
            ],
            key=lambda b: b.get("percentage"),
            reverse=True,
        )

        onderwerpen_ontdubbeld = sorted(
            [
                {
                    "label": onderwerp,
                    "aantal": "{:.2f}".format(
                        float(
                            sum(
                                [
                                    d.get("count")
                                    for kolom in signalen
                                    for d in kolom
                                    if d.get("onderwerp") == onderwerp
                                ]
                            )
                            / sum(
                                [
                                    d.get("count")
                                    for kolom in meldingen
                                    for d in kolom
                                    if d.get("onderwerp") == onderwerp
                                ]
                            )
                        )
                    ),
                }
                for onderwerp in onderwerp_opties
            ],
            key=lambda b: b.get("aantal"),
            reverse=True,
        )
        onderwerpen_ontdubbeld = sorted(
            [
                {**onderwerp, **{"bar": onderwerp.get("aantal")}}
                for onderwerp in onderwerpen_ontdubbeld
            ],
            key=lambda b: b.get("aantal"),
            reverse=True,
        )

        # print(onderwerp_opties)
        print(signalen)
        print(meldingen)
        aantal_meldingen_onderwerp = {
            "title": "Meest gemelde onderwerpen",
            "period_title": self.get_title(),
            "head": ["Onderwerp", "Aantal", "%"],
            "head_percentages": [65, 20, 15],
            "body": onderwerpen,
        }
        aantal_meldingen_wijk = {
            "title": "Wijken met de meeste meldingen",
            "period_title": self.get_title(),
            "head": ["Wijk", "Aantal", "%"],
            "head_percentages": [65, 20, 15],
            "body": wijken,
        }
        aantal_onderwerpen_ontdubbeld = {
            "title": "Meest ontdubbelde onderwerpen",
            "period_title": self.get_title(),
            "head": ["Onderwerp", "verhouding"],
            "head_percentages": [80, 20],
            "body": onderwerpen_ontdubbeld,
        }
        context.update(
            {
                "aantallen_tabs": aantallen_tabs,
                "status_veranderingen_tabs": status_veranderingen_tabs,
                "aantal_meldingen_onderwerp": aantal_meldingen_onderwerp,
                "aantal_meldingen_wijk": aantal_meldingen_wijk,
                "aantal_onderwerpen_ontdubbeld": aantal_onderwerpen_ontdubbeld,
            }
        )
        return context


@method_decorator(
    permission_required("authorisatie.dashboard_bekijken"), name="dispatch"
)
class MeldingenAfgehandeld(Dashboard):
    template_name = "dashboard/afgehandeld/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        afgehandeld = []
        meldingen_service = MeldingenService()
        print(self.x_ticks)
        for tick in self.x_ticks:
            dag = tick.get("start_dt")
            days = tick.get("days")
            status_afgehandeld = meldingen_service.afgehandelde_meldingen(
                datum=dag, days=days
            )
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
