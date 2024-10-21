import calendar
import copy
import statistics
from datetime import datetime, timedelta

from apps.dashboard.querysets import TijdsvakQuerySet
from apps.main.services import TaakRService
from apps.main.templatetags.date_tags import seconds_to_human
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
    def melding_fases(cls):
        return {
            "Midoffice": [
                "openstaand_duur_gemiddeld",
                "controle_duur_gemiddeld",
            ],
            "Uitvoer": [
                "in_behandeling_duur_gemiddeld",
            ],
            "Wachten": [
                "wachten_melder_duur_gemiddeld",
                "pauze_duur_gemiddeld",
            ],
            "Afgehandeld": [
                "geannuleerd_duur_gemiddeld",
                "afgehandeld_duur_gemiddeld",
            ],
        }

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

    @classmethod
    def tabel_wijken_midoffice(cls):
        fase = list(cls.melding_fases().keys())[0]
        return cls.tabel_wijken(fase=fase)

    @classmethod
    def tabel_wijken_uitvoer(cls):
        fase = list(cls.melding_fases().keys())[1]
        return cls.tabel_wijken(fase=fase)

    @classmethod
    def tabel_wijken_wachten(cls):
        fase = list(cls.melding_fases().keys())[2]
        return cls.tabel_wijken(fase=fase)

    @classmethod
    def tabel_wijken_afgehandeld(cls):
        fase = list(cls.melding_fases().keys())[3]
        return cls.tabel_wijken(fase=fase)

    @classmethod
    def tabel_onderwerpen_midoffice(cls):
        fase = list(cls.melding_fases().keys())[0]
        return cls.tabel_onderwerpen(fase=fase)

    @classmethod
    def tabel_onderwerpen_uitvoer(cls):
        fase = list(cls.melding_fases().keys())[1]
        return cls.tabel_onderwerpen(fase=fase)

    @classmethod
    def tabel_onderwerpen_wachten(cls):
        fase = list(cls.melding_fases().keys())[2]
        return cls.tabel_onderwerpen(fase=fase)

    @classmethod
    def tabel_onderwerpen_afgehandeld(cls):
        fase = list(cls.melding_fases().keys())[3]
        return cls.tabel_onderwerpen(fase=fase)

    @classmethod
    def tabel_onderwerpen(cls, fase=None):
        return cls.tabel("onderwerp", fase=fase)

    @classmethod
    def tabel_wijken(cls, fase=None):
        return cls.tabel("wijk", fase=fase)

    @classmethod
    def tabel(cls, data_type="onderwerp", fase=None):
        data_types = {
            "onderwerp": {
                "plural": "onderwerpen",
                "varianten": cls.onderwerpen,
                "filter_type": cls.wijk,
                "filter_naam": "wijk",
            },
            "wijk": {
                "plural": "wijken",
                "varianten": cls.wijken,
                "filter_type": cls.onderwerp,
                "filter_naam": "onderwerp",
            },
        }
        naam_plural = data_types[data_type]["plural"]
        varianten = data_types[data_type]["varianten"]
        filter_type = data_types[data_type]["filter_type"]
        filter_naam = data_types[data_type]["filter_naam"]

        statussen_per_fase = cls.melding_fases()

        alle_statussen = [
            status
            for f, statussen in statussen_per_fase.items()
            for status in statussen
        ]
        fase = None if fase not in list(statussen_per_fase.keys()) else fase
        statussen = statussen_per_fase[fase] if fase else alle_statussen

        def tijdsvak_status_gemiddelden(_afgehandeld, onderwerp, _statussen):
            status_gemiddelden_totaal = []
            for i, tijdsvak in enumerate(_afgehandeld):
                melding_aantal = 0
                tijdsvak_total = []
                for status in _statussen:
                    status_gemiddelden = []
                    for d in tijdsvak:
                        if onderwerp == d.get(data_type) and d.get(status) is not None:
                            melding_aantal += d.get("melding_aantal")
                            status_gemiddelden = status_gemiddelden + [
                                float(d.get(status))
                                for i in range(0, d.get("melding_aantal"))
                            ]
                    tijdsvak_total.append(average(status_gemiddelden))
                status_gemiddelden_totaal = status_gemiddelden_totaal + [
                    sum(tijdsvak_total) for i in range(0, melding_aantal)
                ]
            return average(status_gemiddelden_totaal)

        data = copy.deepcopy(cls.tijdsvakken if hasattr(cls, "tijdsvakken") else [])

        data = (
            [
                [
                    variant
                    for variant in tijdsvak
                    if variant.get(filter_naam) == filter_type
                ]
                for tijdsvak in data
            ]
            if filter_type
            else data
        )

        table = sorted(
            [
                {
                    "label": variant_naam,
                    "aantal": tijdsvak_status_gemiddelden(
                        data, variant_naam, statussen
                    ),
                    "totaal_aantal": tijdsvak_status_gemiddelden(
                        data, variant_naam, alle_statussen
                    ),
                }
                for variant_naam in varianten
            ],
            key=lambda b: b.get("aantal"),
            reverse=True,
        )

        table = [
            {
                data_type.title(): variant.get("label"),
                "Duur": seconds_to_human(variant.get("aantal")),
                "bar": round(
                    float(variant.get("aantal") / table[0].get("aantal")) * 100
                )
                if table and table[0].get("aantal")
                else 0,
            }
            for variant in table
        ]

        filters = (
            f" filters: {cls.onderwerp if cls.onderwerp else ''}, {cls.wijk if cls.wijk else ''}"
            if cls.onderwerp or cls.wijk
            else ""
        )
        title = f"Fase '{fase}'" if fase else f"Totaal voor {naam_plural}"
        title_unique = (
            f"Doorlooptijden fase '{fase}' voor {naam_plural}"
            if fase
            else f"Doorlooptijden totaal voor {naam_plural}"
        )
        title_unique = (
            f"{cls.type}-{cls.status} {title_unique}: {cls.periode_titel}{filters}"
        )
        return render_to_string(
            "charts/dashboard_item.html",
            {
                "title": title,
                "title_unique": title_unique,
                "head": [data_type.title(), "Duur"],
                "body": table,
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

    @classmethod
    def chart_tabs(cls):
        labels = [t.get("label") for t in cls.x_ticks]
        wijk = cls.wijk
        onderwerp = cls.onderwerp
        cls.wijken
        cls.wijken_noord
        cls.wijken_zuid

        data = copy.deepcopy(cls.tijdsvakken if hasattr(cls, "tijdsvakken") else [])

        tabs = [
            {
                "begin_status": "openstaand",
                "eind_status": "in_behandeling",
                "titel": "Openstaand -> in behandeling",
            },
            {
                "begin_status": "in_behandeling",
                "eind_status": "controle",
                "titel": "In behandeling -> controle",
            },
            {
                "begin_status": "controle",
                "eind_status": "afgehandeld",
                "titel": "Controle -> afgehandeld",
            },
        ]
        tabs = [
            {
                **tab,
                **{
                    "datasets": [
                        {
                            "type": "line",
                            "label": "gemiddelde duur",
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
                        "barPercentage": "0.2",
                        "borderColor": "#00811F",
                        "fill": True,
                        "backgroundColor": "rgba(0,200,100,0.1)",
                        "data": [
                            average(
                                [
                                    float(d.get("duur_seconden_gemiddeld"))
                                    for d in dag
                                    if d.get("begin_status") == tab.get("begin_status")
                                    and d.get("eind_status") == tab.get("eind_status")
                                    and (
                                        not onderwerp or onderwerp == d.get("onderwerp")
                                    )
                                    and (not wijk or wijk == d.get("wijk"))
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
                    "aantal": int(
                        average(
                            [
                                average([d for d in dataset.get("data", []) if d != 0])
                                for dataset in tab.get("datasets", [])
                            ]
                        )
                    )
                },
            }
            for tab in tabs
        ]
        return render_to_string(
            "charts/base_chart.html",
            {
                "tabs": tabs,
                "title": "Doorlooptijden per status verandering",
                "period_title": cls.periode_titel,
                "description": "",
                "data_type": "duration",
            },
        )


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
