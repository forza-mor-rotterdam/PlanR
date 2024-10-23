import calendar
import copy
import logging
from datetime import datetime, timedelta

import isoweek
from apps.dashboard.forms import DashboardForm
from apps.dashboard.models import (
    DoorlooptijdenAfgehandeldeMeldingen,
    NieuweMeldingAantallen,
    NieuweSignaalAantallen,
)
from apps.dashboard.models import NieuweTaakopdrachten as NieuweTaakopdrachtenModel
from apps.dashboard.models import (
    StatusVeranderingDuurMeldingen,
    TaakopdrachtDoorlooptijden,
    TaaktypeAantallenPerMelding,
    Tijdsvak,
)
from apps.main.constanten import (
    DAGEN_VAN_DE_WEEK_KORT,
    MAANDEN,
    MAANDEN_KORT,
    PDOK_WIJKEN,
)
from apps.main.services import OnderwerpenService
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
    tijdsvak_classes = []

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
        self.tijdsvak_periode = Tijdsvak.PeriodeOpties.DAG
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
                    self.tijdsvak_periode = Tijdsvak.PeriodeOpties.MAAND
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

        onderwerpen_service = OnderwerpenService()

        for cls in self.tijdsvak_classes:
            cls.onderwerpen = [
                c.get("name") for c in onderwerpen_service.get_onderwerpen()
            ]
            cls.wijken = [c.get("wijknaam") for c in PDOK_WIJKEN]
            cls.wijken_noord = [
                wijk.get("wijknaam")
                for wijk in PDOK_WIJKEN
                if wijk.get("stadsdeel") == "Noord"
            ]
            cls.wijken_zuid = [
                wijk.get("wijknaam")
                for wijk in PDOK_WIJKEN
                if wijk.get("stadsdeel") == "Zuid"
            ]
            cls.wijk = self.wijk
            cls.onderwerp = self.onderwerp
            cls.x_ticks = self.x_ticks
            cls.periode_titel = self.title
            cls.type = self.kwargs.get("type")
            cls.status = self.kwargs.get("status")
            cls.tijdsvakken = list(
                cls.objects.filter(
                    periode=self.tijdsvak_periode,
                    start_datumtijd__gte=self.x_ticks[0].get("start_dt"),
                    start_datumtijd__lte=self.x_ticks[-1].get("start_dt"),
                ).values_list("resultaat", flat=True)
            )

        context.update({cls.__name__: cls for cls in self.tijdsvak_classes})

        return context


@method_decorator(
    permission_required("authorisatie.dashboard_bekijken", raise_exception=True),
    name="dispatch",
)
class NieuweMeldingen(Dashboard):
    template_name = "dashboard/nieuwe/dashboard.html"

    tijdsvak_classes = [
        NieuweMeldingAantallen,
        NieuweSignaalAantallen,
        DoorlooptijdenAfgehandeldeMeldingen,
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        NieuweMeldingAantallen.signaal_data = NieuweSignaalAantallen.tijdsvakken
        NieuweMeldingAantallen.afgehandeld_tijdsvakken = (
            DoorlooptijdenAfgehandeldeMeldingen.tijdsvakken
        )

        return context


@method_decorator(
    permission_required("authorisatie.dashboard_bekijken", raise_exception=True),
    name="dispatch",
)
class MeldingenAfgehandeld(Dashboard):
    template_name = "dashboard/afgehandeld/dashboard.html"
    tijdsvak_classes = [
        DoorlooptijdenAfgehandeldeMeldingen,
        StatusVeranderingDuurMeldingen,
    ]


@method_decorator(
    permission_required("authorisatie.dashboard_bekijken", raise_exception=True),
    name="dispatch",
)
class TaaktypeAantallen(Dashboard):
    template_name = "dashboard/taken/taaktype_aantallen.html"

    tijdsvak_classes = [
        TaaktypeAantallenPerMelding,
    ]


@method_decorator(
    permission_required("authorisatie.dashboard_bekijken", raise_exception=True),
    name="dispatch",
)
class NieuweTaakopdrachten(Dashboard):
    template_name = "dashboard/taken/nieuwe_taakopdrachten.html"
    tijdsvak_classes = [
        NieuweTaakopdrachtenModel,
        TaakopdrachtDoorlooptijden,
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        TaakopdrachtDoorlooptijden.nieuwe_taakopdrachten = (
            NieuweTaakopdrachtenModel.tijdsvakken
        )

        return context
