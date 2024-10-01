import calendar
import copy
import logging
from datetime import datetime, timedelta

import isoweek
from apps.dashboard.forms import DashboardForm
from apps.dashboard.tables import (
    get_aantallen_tabs,
    get_afgehandeld_tabs,
    get_meldingen_nieuw_vs_afgehandeld_tabs,
    get_nieuwe_taakopdrachten_tabs,
    get_status_veranderingen_tabs,
    get_taaktype_aantallen_per_melding_tabs,
    get_taken_nieuw_vs_afgehandeld_tabs,
    top_doorlooptijden_per_onderwerp,
    top_doorlooptijden_per_wijk,
    top_taaktype_aantallen,
    top_vijf_aantal_meldingen_onderwerp,
    top_vijf_aantal_meldingen_wijk,
    top_vijf_aantal_onderwerpen_ontdubbeld,
)
from apps.main.constanten import (
    DAGEN_VAN_DE_WEEK_KORT,
    MAANDEN,
    MAANDEN_KORT,
    PDOK_WIJKEN,
)
from apps.services.meldingen import MeldingenService
from apps.services.onderwerpen import OnderwerpenService
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
    success_url = "/dashboard/"
    periode = None
    title = None
    week = maand = jaar = onderwerp = wijk = None

    def get_success_url(self):
        return self.request.path

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def form_valid(self, form):
        self.onderwerp = form.cleaned_data.get("onderwerp")
        self.wijk = form.cleaned_data.get("wijk")
        return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = {
            "initial": self.get_initial(),
            "prefix": self.get_prefix(),
        }
        if self.request.method in ("GET",):
            kwargs.update(
                {
                    "data": self.request.GET,
                }
            )
        return kwargs

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
            return f"maand {MAANDEN[int(maand_param) - 1]} {int(jaar_param)}"

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
                    "label": f"{DAGEN_VAN_DE_WEEK_KORT[dag.weekday()]} {dag.strftime('%-d')} {MAANDEN_KORT[dag.month - 1]}",
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
                    "label": f"{dag.strftime('%-d')} {MAANDEN_KORT[dag.month - 1]}",
                }
                for dag in dagen
            ]
            return ticks

        if self.jaar and self.PeriodeOpties.JAAR:
            maanden = [
                datetime(int(jaar_param), maand + 1, 1) for maand in range(0, 12)
            ]
            ticks = [
                {
                    "start_dt": dag,
                    "type": "maand",
                    "days": calendar.monthrange(dag.year, dag.month)[1],
                    "label": f"{MAANDEN[dag.month - 1]}",
                }
                for dag in maanden
            ]
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
            f"{MAANDEN[dt.month - 1]} {dt.year}",
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
                [f"{MAANDEN[int(maand_param) - 1]} {int(jaar_param)}", 0],
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
        link_data = [
            ["meldingen", "nieuw", "Nieuwe meldingen"],
            ["meldingen", "afgehandeld", "Afgehandelde meldingen"],
            ["taken", "aantallen", "Taken aantallen"],
            ["taken", "nieuw", "Nieuwe taken"],
        ]

        def get_url(type, status):
            try:
                return reverse(
                    "dashboard",
                    kwargs={
                        **copy.deepcopy(self.kwargs),
                        **{
                            "type": type,
                            "status": status,
                        },
                    },
                )
            except Exception:
                return

        statussen = [
            [
                d[2],
                ""
                if self.kwargs.get("status") == d[1] and self.kwargs.get("type") == d[0]
                else get_url(d[0], d[1]),
            ]
            for d in link_data
            if get_url(d[0], d[1])
        ]

        return statussen

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
                "wijk": self.wijk,
                "onderwerp": self.onderwerp,
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
        afgehandeld = []
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

            status_afgehandeld = meldingen_service.afgehandelde_meldingen(
                datum=dag, days=days
            )
            afgehandeld.append(status_afgehandeld)
            meldingen.append(melding_aantallen)
            signalen.append(signaal_aantallen)

        aantallen_tabs = get_aantallen_tabs(
            meldingen,
            signalen,
            ticks=self.x_ticks,
            onderwerp=self.onderwerp,
            wijk=self.wijk,
        )
        nieuw_vs_afgehandeld_tabs = get_meldingen_nieuw_vs_afgehandeld_tabs(
            meldingen,
            afgehandeld,
            ticks=self.x_ticks,
            onderwerp=self.onderwerp,
            wijk=self.wijk,
        )

        onderwerp_opties = list(
            set([d.get("onderwerp") for kolom in meldingen for d in kolom])
        )
        wijk_opties = list(set([d.get("wijk") for kolom in meldingen for d in kolom]))

        context.update(
            {
                "aantallen_tabs": aantallen_tabs,
                "nieuw_vs_afgehandeld_tabs": nieuw_vs_afgehandeld_tabs,
                "aantal_meldingen_onderwerp": top_vijf_aantal_meldingen_onderwerp(
                    meldingen, onderwerp_opties, wijk=self.wijk
                ),
                "aantal_meldingen_wijk": top_vijf_aantal_meldingen_wijk(
                    meldingen, wijk_opties, onderwerp=self.onderwerp
                ),
                "aantal_onderwerpen_ontdubbeld": top_vijf_aantal_onderwerpen_ontdubbeld(
                    meldingen, signalen, onderwerp_opties, wijk=self.wijk
                ),
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

        onderwerpen_service = OnderwerpenService()
        onderwerpen = onderwerpen_service.get_onderwerpen()
        valide_wijken = [c.get("wijknaam") for c in PDOK_WIJKEN]

        afgehandeld = []
        veranderingen = []
        meldingen_service = MeldingenService()
        for tick in self.x_ticks:
            dag = tick.get("start_dt")
            days = tick.get("days")
            status_afgehandeld = meldingen_service.afgehandelde_meldingen(
                datum=dag, days=days
            )
            status_veranderingen = meldingen_service.status_veranderingen(
                datum=dag, days=days
            )
            afgehandeld.append(status_afgehandeld)
            veranderingen.append(status_veranderingen)

        afgehandeld_tabs = get_afgehandeld_tabs(
            afgehandeld, ticks=self.x_ticks, onderwerp=self.onderwerp, wijk=self.wijk
        )
        status_veranderingen_tabs = get_status_veranderingen_tabs(
            veranderingen, ticks=self.x_ticks, onderwerp=self.onderwerp, wijk=self.wijk
        )
        valide_onderwerpen = [c.get("name") for c in onderwerpen]
        doorlooptijden_onderwerp = [
            top_doorlooptijden_per_onderwerp(
                afgehandeld,
                valide_onderwerpen=valide_onderwerpen,
                wijk=self.wijk,
                aantal=10,
            )
        ]
        doorlooptijden_wijk = [
            top_doorlooptijden_per_wijk(
                afgehandeld,
                valide_wijken=valide_wijken,
                onderwerp=self.onderwerp,
                aantal=10,
            )
        ]
        for fase in ["Midoffice", "Uitvoer", "Wachten", "Afgehandeld"]:
            doorlooptijden_onderwerp.append(
                top_doorlooptijden_per_onderwerp(
                    afgehandeld,
                    valide_onderwerpen=valide_onderwerpen,
                    wijk=self.wijk,
                    fase=fase,
                    aantal=10,
                )
            )
            doorlooptijden_wijk.append(
                top_doorlooptijden_per_wijk(
                    afgehandeld,
                    valide_wijken=valide_wijken,
                    onderwerp=self.onderwerp,
                    fase=fase,
                    aantal=10,
                )
            )

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
                "status_veranderingen_tabs": status_veranderingen_tabs,
                "doorlooptijden_onderwerp": doorlooptijden_onderwerp,
                "doorlooptijden_wijk": doorlooptijden_wijk,
                "stacked_bars_options": stacked_bars_options,
            }
        )
        return context


@method_decorator(
    permission_required("authorisatie.dashboard_bekijken"), name="dispatch"
)
class TaaktypeAantallen(Dashboard):
    template_name = "dashboard/taken/taaktype_aantallen.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        taaktype_aantallen_per_melding = []
        meldingen_service = MeldingenService()
        for tick in self.x_ticks:
            dag = tick.get("start_dt")
            days = tick.get("days")
            taaktype_aantallen_per_melding_tijdsvak = (
                meldingen_service.taaktype_aantallen_per_melding(
                    datum=dag, days=days, force_cache=False
                )
            )
            taaktype_aantallen_per_melding.append(
                taaktype_aantallen_per_melding_tijdsvak
            )

        taaktype_aantallen_per_melding_tabs = get_taaktype_aantallen_per_melding_tabs(
            taaktype_aantallen_per_melding,
            ticks=self.x_ticks,
            onderwerp=self.onderwerp,
            wijk=self.wijk,
        )
        top_10_taaktype_aantallen = top_taaktype_aantallen(
            taaktype_aantallen_per_melding,
            onderwerp=self.onderwerp,
            wijk=self.wijk,
            aantal=10,
        )

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
                "taaktype_aantallen_per_melding_tabs": taaktype_aantallen_per_melding_tabs,
                "top_10_taaktype_aantallen": top_10_taaktype_aantallen,
                "stacked_bars_options": stacked_bars_options,
            }
        )
        return context


class NieuweTaakopdrachten(Dashboard):
    template_name = "dashboard/taken/nieuwe_taakopdrachten.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        nieuwe_taakopdrachten = []
        taakopdracht_doorlooptijden = []
        meldingen_service = MeldingenService()
        for tick in self.x_ticks:
            dag = tick.get("start_dt")
            days = tick.get("days")
            nieuwe_taakopdrachten_tijdsvak = meldingen_service.nieuwe_taakopdrachten(
                datum=dag, days=days, force_cache=False
            )
            taakopdracht_doorlooptijden_tijdsvak = (
                meldingen_service.taakopdracht_doorlooptijden(
                    datum=dag, days=days, force_cache=False
                )
            )
            nieuwe_taakopdrachten.append(nieuwe_taakopdrachten_tijdsvak)
            taakopdracht_doorlooptijden.append(taakopdracht_doorlooptijden_tijdsvak)

        nieuwe_taakopdrachten_tabs = get_nieuwe_taakopdrachten_tabs(
            nieuwe_taakopdrachten,
            ticks=self.x_ticks,
            onderwerp=self.onderwerp,
            wijk=self.wijk,
        )
        taken_nieuw_vs_afgehandeld_tabs = get_taken_nieuw_vs_afgehandeld_tabs(
            nieuwe_taakopdrachten,
            taakopdracht_doorlooptijden,
            ticks=self.x_ticks,
            onderwerp=self.onderwerp,
            wijk=self.wijk,
        )

        context.update(
            {
                "nieuwe_taakopdrachten_tabs": nieuwe_taakopdrachten_tabs,
                "taken_nieuw_vs_afgehandeld_tabs": taken_nieuw_vs_afgehandeld_tabs,
            }
        )
        return context
