import calendar
import copy
import statistics
from datetime import datetime, timedelta

from apps.dashboard.querysets import TijdsvakQuerySet
from apps.services.taakr import TaakRService
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from utils.models import BasisModel


def average(lst):
    try:
        return statistics.mean([li for li in lst if not li == 0])
    except Exception:
        ...
    return 0


class Databron(BasisModel):
    class BrontypeOpties(models.TextChoices):
        DOORLOOPTIJDEN_AFGEHANDELDE_MELDINGEN = (
            "doorlooptijden_afgehandelde_meldingen",
            "Doorlooptijden afgehandelde meldingen",
        )
        STATUS_VERANDERING_DUUR_MELDINGEN = (
            "status_verandering_duur_meldingen",
            "Status verandering duur voor meldingen",
        )
        NIEUWE_MELDING_AANTALLEN = (
            "nieuwe_melding_aantallen",
            "Nieuwe melding aantallen",
        )
        NIEUWE_SIGNAAL_AANTALLEN = (
            "nieuwe_signaal_aantallen",
            "Nieuwe signaal aantallen",
        )
        NIEUWE_TAAKOPDRACHTEN = "nieuwe_taakopdrachten", "Nieuwe taakopdrachten"
        TAAKTYPE_AANTALLEN_PER_MELDING = (
            "taaktype_aantallen_per_melding",
            "Taaktype aantallen per melding",
        )
        TAAKOPDRACHT_DOORLOOPTIJDEN = (
            "taakopdracht_doorlooptijden",
            "Taakopdracht doorlooptijden",
        )

    brontype = models.CharField(
        max_length=100,
        choices=BrontypeOpties.choices,
        unique=True,
    )
    url = models.URLField()
    start_datumtijd_param = models.CharField(
        max_length=50,
        default="aangemaakt_op_gte",
    )
    eind_datumtijd_param = models.CharField(
        max_length=50,
        default="aangemaakt_op_lt",
    )

    def __str__(self) -> str:
        return self.brontype

    class Meta:
        verbose_name = "Databron"
        verbose_name_plural = "Databronnen"


class Tijdsvak(BasisModel):
    periode_titel = None
    onderwerp = None
    onderwerpen = []
    wijk = None
    wijken = []
    wijken_noord = []
    wijken_zuid = []
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

    class PeriodeOpties(models.TextChoices):
        DAG = "dag", "Dag"
        WEEK = "week", "Week"
        MAAND = "maan", "Maand"

    start_datumtijd = models.DateTimeField()
    eind_datumtijd = models.DateTimeField()
    valide_data = models.BooleanField(
        default=False,
    )
    resultaat = models.JSONField(
        default=list,
    )
    periode = models.CharField(
        max_length=50,
        choices=PeriodeOpties.choices,
        default=PeriodeOpties.DAG,
    )
    databron = models.ForeignKey(
        to="dashboard.Databron",
        related_name="tijdsvakken_voor_databron",
        on_delete=models.CASCADE,
    )

    objects = TijdsvakQuerySet()

    class Meta:
        verbose_name = "Tijdsvak"
        verbose_name_plural = "Tijdsvakken"
        unique_together = (
            "databron",
            "start_datumtijd",
            "eind_datumtijd",
        )
        ordering = ["start_datumtijd"]

    def save(self, *args, **kwargs):
        sd = self.start_datumtijd
        ed = self.eind_datumtijd
        if self.pk:
            vorig_tijdsvak = Tijdsvak.objects.get(pk=self.pk)
            if (
                vorig_tijdsvak.start_datumtijd != sd
                or vorig_tijdsvak.eind_datumtijd != ed
                or vorig_tijdsvak.periode != self.periode
            ):
                raise ValidationError("The read_only_field can not be changed")
        else:
            sd = self.start_datumtijd = datetime(sd.year, sd.month, sd.day)
            self.eind_datumtijd = sd + timedelta(days=1)
            if self.periode == Tijdsvak.PeriodeOpties.WEEK:
                self.start_datumtijd = sd - timedelta(
                    days=self.start_datumtijd.isoweekday() % 7
                )
                self.eind_datumtijd = self.start_datumtijd + timedelta(days=7)
            elif self.periode == Tijdsvak.PeriodeOpties.MAAND:
                self.start_datumtijd = datetime(sd.year, sd.month, 1)
                self.eind_datumtijd = self.start_datumtijd + timedelta(
                    days=calendar.monthrange(sd.year, sd.month)[1]
                )

        super().save(*args, **kwargs)


class DoorlooptijdenAfgehandeldeMeldingen(Tijdsvak):
    """
    Basis klasse voor doorlooptijden_afgehandelde_meldingen informatie.
    """

    def save(self, *args, **kwargs):
        databron, _ = Databron.objects.get_or_create(
            brontype=Databron.BrontypeOpties.DOORLOOPTIJDEN_AFGEHANDELDE_MELDINGEN
        )
        self.databron = databron
        super().save(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = "Doorlooptijden afgehandelde meldingen"
        verbose_name_plural = "Doorlooptijden afgehandelde meldingen"

    @classmethod
    def stacked_chart_tabs(cls):
        labels = [t.get("label") for t in cls.x_ticks]
        wijk = cls.wijk
        onderwerp = cls.onderwerp
        wijken = cls.wijken
        cls.onderwerpen
        wijken_noord = cls.wijken_noord
        wijken_zuid = cls.wijken_zuid

        data = copy.deepcopy(cls.tijdsvakken if hasattr(cls, "tijdsvakken") else [])

        def tijdsvak_status_gemiddelden(tijdsvak, statussen, tab, dag_index):
            status_gemiddelden_totaal = []
            for status in statussen:
                status_gemiddelden = []
                for d in tijdsvak:
                    if (
                        bool(d.get("wijk") in tab.get("wijken"))
                        != tab.get("wijk_not_in")
                        and d.get(status) is not None
                    ):
                        status_gemiddelden = status_gemiddelden + [
                            float(d.get(status))
                            for i in range(0, d.get("melding_aantal"))
                        ]
                status_gemiddelden_totaal.append(average(status_gemiddelden))
            return sum(status_gemiddelden_totaal)

        data = (
            [
                [variant for variant in tijdsvak if variant.get("wijk") == wijk]
                for tijdsvak in data
            ]
            if wijk
            else data
        )
        data = (
            [
                [
                    variant
                    for variant in tijdsvak
                    if variant.get("onderwerp") == onderwerp
                ]
                for tijdsvak in data
            ]
            if onderwerp
            else data
        )
        tabs = (
            [
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
            ]
            if not wijk
            else [
                {
                    "wijken": [w for w in wijken if wijk == w],
                    "wijk_not_in": False,
                    "titel": wijk,
                }
            ]
        )
        tabs = [
            {
                **tab,
                **{
                    "datasets": [
                        {
                            "backgroundColor": "#00580c",
                            "label": "Midoffice",
                            "statussen": [
                                "openstaand_duur_gemiddeld",
                                "controle_duur_gemiddeld",
                            ],
                            "bron": data,
                        },
                        {
                            "backgroundColor": "#00811f",
                            "label": "Uitvoer",
                            "statussen": [
                                "in_behandeling_duur_gemiddeld",
                            ],
                            "bron": data,
                        },
                        {
                            "backgroundColor": "#e3f4dd",
                            "label": "Wachten",
                            "statussen": [
                                "wachten_melder_duur_gemiddeld",
                                "pauze_duur_gemiddeld",
                            ],
                            "bron": data,
                        },
                        {
                            "backgroundColor": "#eeeeee",
                            "label": "Afgehandeld",
                            "statussen": [
                                "geannuleerd_duur_gemiddeld",
                                "afgehandeld_duur_gemiddeld",
                            ],
                            "bron": data,
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
                "type": "bar",
                "datasets": [
                    {
                        "type": "bar",
                        "label": dataset.get("label"),
                        "backgroundColor": dataset.get("backgroundColor"),
                        "borderColor": "#ffffff",
                        "fill": True,
                        "data": [
                            tijdsvak_status_gemiddelden(
                                dag, dataset.get("statussen", []), tab, i
                            )
                            for i, dag in enumerate(dataset.get("bron"))
                        ],
                    }
                    for dataset in tab.get("datasets", [])
                ],
            }
            for tab in tabs
        ]

        def get_average(tbl):
            l2 = list(zip(*tbl))
            l2t = [sum([nn for nn in dd]) for dd in l2]
            l2tt = [d for d in l2t if d != 0]
            return average(l2tt)

        for tab in tabs:
            tab["aantal"] = get_average(
                [
                    [d for d in dataset.get("data", [])]
                    for dataset in tab.get("datasets", [])
                ]
            )
        return render_to_string(
            "charts/base_chart.html",
            {
                "tabs": tabs,
                "title": "Doorlooptijden",
                "period_title": cls.periode_titel,
                "description": "Midoffice duur is bepaald door de optelling van alle tijd dat de melding in controle staat en de optelling van dat de melding op openstaand staat. De uitvoer duur wordt bepaald door de optellingen van alle keren dat de melding in behandeling staat. Wachten wordt berekend door de duur van alle pauze statussen op te tellen. De afgehandeld duur wordt bepaald doordat de melding heropend is, dus dan heeft de melding meer dan 1 afgehandeld status.",
                "data_type": "duration",
                "options": cls.stacked_bars_options,
            },
        )


class StatusVeranderingDuurMeldingen(Tijdsvak):
    """
    Basis klasse voor status_verandering_duur_meldingen informatie.
    """

    def save(self, *args, **kwargs):
        databron, _ = Databron.objects.get_or_create(
            brontype=Databron.BrontypeOpties.STATUS_VERANDERING_DUUR_MELDINGEN
        )
        self.databron = databron
        super().save(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = "Status verandering duur voor meldingen"
        verbose_name_plural = "Status verandering duur voor meldingen"


class NieuweMeldingAantallen(Tijdsvak):
    """
    Basis klasse voor nieuwe_melding_aantallen informatie.
    """

    def save(self, *args, **kwargs):
        databron, _ = Databron.objects.get_or_create(
            brontype=Databron.BrontypeOpties.NIEUWE_MELDING_AANTALLEN
        )
        self.databron = databron
        super().save(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = "Nieuwe melding aantallen"
        verbose_name_plural = "Nieuwe melding aantallen"


class NieuweSignaalAantallen(Tijdsvak):
    """
    Basis klasse voor nieuwe_signaal_aantallen informatie.
    """

    def save(self, *args, **kwargs):
        databron, _ = Databron.objects.get_or_create(
            brontype=Databron.BrontypeOpties.NIEUWE_SIGNAAL_AANTALLEN
        )
        self.databron = databron
        super().save(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = "Nieuwe signaal aantallen"
        verbose_name_plural = "Nieuwe signaal aantallen"


class NieuweTaakopdrachten(Tijdsvak):
    """
    Basis klasse voor nieuwe_taakopdrachten informatie.
    """

    def save(self, *args, **kwargs):
        databron, _ = Databron.objects.get_or_create(
            brontype=Databron.BrontypeOpties.NIEUWE_TAAKOPDRACHTEN
        )
        self.databron = databron
        super().save(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = "Nieuwe taakopdrachten"
        verbose_name_plural = "Nieuwe taakopdrachten"

    @classmethod
    def stacked_chart_tabs(cls):
        labels = [t.get("label") for t in cls.x_ticks]
        wijk = cls.wijk
        onderwerp = cls.onderwerp
        wijken = cls.wijken
        wijken_noord = cls.wijken_noord
        wijken_zuid = cls.wijken_zuid

        taakr_service = TaakRService()
        afdelingen = taakr_service.get_afdelingen()
        taaktypes = taakr_service.get_taaktypes()
        onderdelen = ("schoon", "heel", "veilig")
        externe_afdelingen = [
            afdeling for afdeling in afdelingen if not afdeling["onderdeel"]
        ]
        onderdeel_taaktypes = {
            onderdeel: [
                taaktype["_links"]["taakapplicatie_taaktype_url"]
                for afdeling in afdelingen
                for taaktype in taaktypes
                if afdeling["onderdeel"] == onderdeel
                and afdeling["_links"]["self"] in taaktype["afdelingen"]
            ]
            for onderdeel in onderdelen
        }
        onderdeel_taaktypes["extern"] = [
            taaktype["_links"]["taakapplicatie_taaktype_url"]
            for afdeling in externe_afdelingen
            for taaktype in taaktypes
            if afdeling["_links"]["self"] in taaktype["afdelingen"]
        ]
        onderdeel_taaktypes["overig"] = [
            taaktype["_links"]["taakapplicatie_taaktype_url"]
            for taaktype in taaktypes
            if not taaktype["afdelingen"]
        ]

        data = copy.deepcopy(cls.tijdsvakken if hasattr(cls, "tijdsvakken") else [])

        tabs = (
            [
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
            if not wijk
            else [
                {
                    "wijken": [w for w in wijken if wijk == w],
                    "wijk_not_in": False,
                    "titel": wijk,
                }
            ]
        )
        tabs = [
            {
                **tab,
                **{
                    "datasets": [
                        {
                            "type": "bar",
                            "label": "Schoon",
                            "backgroundColor": "#FFA500",
                            "onderdeel": "schoon",
                            "bron": data,
                        },
                        {
                            "type": "bar",
                            "label": "Heel",
                            "backgroundColor": "#00811f",
                            "onderdeel": "heel",
                            "bron": data,
                        },
                        {
                            "type": "bar",
                            "label": "Veilg",
                            "backgroundColor": "#0000ff",
                            "onderdeel": "veilig",
                            "bron": data,
                        },
                        {
                            "type": "bar",
                            "label": "Extern",
                            "backgroundColor": "#bbb",
                            "onderdeel": "extern",
                            "bron": data,
                        },
                        {
                            "type": "bar",
                            "label": "Overig",
                            "backgroundColor": "#ddd",
                            "onderdeel": "overig",
                            "bron": data,
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
                        "backgroundColor": dataset.get("backgroundColor"),
                        "fill": True,
                        "data": [
                            sum(
                                [
                                    d.get("taakopdracht_aantal")
                                    for d in dag
                                    if bool(d.get("wijk") in tab.get("wijken"))
                                    != bool(tab.get("wijk_not_in"))
                                    and (
                                        not onderwerp or onderwerp == d.get("onderwerp")
                                    )
                                    and d["taaktype"]
                                    in onderdeel_taaktypes[dataset["onderdeel"]]
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
                    "aantal": sum(
                        [
                            sum(dataset.get("data", []))
                            for dataset in tab.get("datasets", [])
                        ]
                    )
                },
            }
            for tab in tabs
        ]
        return render_to_string(
            "charts/base_chart.html",
            {
                "tabs": tabs,
                "title": "Nieuwe taken",
                "period_title": cls.periode_titel,
                "description": "De taken zijn onderverdeeld in afdelingen. De taken die (nog) niet ondervdeeld zijn, worden hier getoond onder 'Overig'. Als in de afdeling het onderdeel ontbreekt, wordt de taak onderverdeeld onder 'Extern'. De overige taken worden onverdeeld in schoon, heel en veilig).",
                "options": cls.stacked_bars_options,
            },
        )


class TaaktypeAantallenPerMelding(Tijdsvak):
    """
    Basis klasse voor taaktype_aantallen_per_melding informatie.
    """

    def save(self, *args, **kwargs):
        databron, _ = Databron.objects.get_or_create(
            brontype=Databron.BrontypeOpties.TAAKTYPE_AANTALLEN_PER_MELDING
        )
        self.databron = databron
        super().save(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = "Taaktype aantallen per melding"
        verbose_name_plural = "Taaktype aantallen per melding"


class TaakopdrachtDoorlooptijden(Tijdsvak):
    """
    Basis klasse voor taakopdracht_doorlooptijden informatie.
    """

    def save(self, *args, **kwargs):
        databron, _ = Databron.objects.get_or_create(
            brontype=Databron.BrontypeOpties.TAAKOPDRACHT_DOORLOOPTIJDEN
        )
        self.databron = databron
        super().save(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = "Taakopdracht doorlooptijden"
        verbose_name_plural = "Taakopdracht doorlooptijden"
