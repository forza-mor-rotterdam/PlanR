import string

from apps.main.constanten import VERTALINGEN
from apps.services.onderwerpen import (
    OnderwerpenService,
    render_onderwerp,
    render_onderwerp_groepen,
)
from django.http import QueryDict
from django.template.loader import get_template
from django.urls import reverse
from django.utils.safestring import mark_safe
from utils.datetime import stringdatetime_naar_datetime
from utils.diversen import string_based_lookup


class StandaardKolom:
    _view_name = "melding_lijst"
    _ordering_key = "ordering"
    _key = None
    _kolom_hoofd = None
    _kolom_inhoud = None
    _ordering_value = ""
    _th_standaard_classes = ""
    _td_standaard_classes = ""
    context = {}

    def __init__(self, context):
        self.context = context

    @classmethod
    def key(cls):
        return cls._key

    def has_ordering(self):
        return bool(self._ordering_value)

    def ordering_up(self):
        return self.context.get("ordering") == "up"

    def ordering(self):
        up = self.ordering_up()
        if not self.has_ordering():
            return False
        return f'{"" if up else "-"}{self._ordering_value}'

    def th_label(self):
        return self._kolom_hoofd

    def td_label(self):
        return string_based_lookup(self.context, self._kolom_inhoud)

    def th_inhoud(self):
        if not self._ordering_value:
            return self.th_label()
        return self.sortable_a_tag()

    def td_inhoud(self):
        return self.td_label()

    def sortable_querystring(self):
        qd = QueryDict("", mutable=True)
        qd.update(self.context.get("request", {}).GET)
        if self._ordering_value == qd.get(self._ordering_key):
            qd[self._ordering_key] = f"-{self._ordering_value}"
        else:
            qd[self._ordering_key] = self._ordering_value
        return qd.urlencode()

    def sortable_a_href(self):
        return f"{reverse(self._view_name)}?{self.sortable_querystring()}"

    def sortable_a_tag(self):
        return mark_safe(
            f'<a href="{self.sortable_a_href()}" role="button">{self.th_label()}</a>'
        )

    def th_standaard_classes(self):
        return f"{self._th_standaard_classes} "

    def td_standaard_classes(self):
        return f"{self._td_standaard_classes} "

    def th_classes(self):
        if not self._ordering_value:
            return ""
        qd = QueryDict("", mutable=True)
        qd.update(self.context.get("request", {}).GET)

        up = qd.get(self._ordering_key) == self._ordering_value
        down = qd.get(self._ordering_key) == f"-{self._ordering_value}"
        if up:
            return "sorting sorting--up"
        if down:
            return "sorting sorting--down"
        return "sorting"

    def td_classes(self):
        return ""

    @property
    def th(self):
        return mark_safe(
            f'<th class="{self.th_standaard_classes()}{self.th_classes()}">{self.th_inhoud()}</th>'
        )

    @property
    def td(self):
        return mark_safe(
            f'<td class="{self.td_standaard_classes()}{self.td_classes()}">{self.td_inhoud()}</td>'
        )


class MSBNummerKolom(StandaardKolom):
    _key = "msb_nummer"
    _kolom_hoofd = "MSB Nummer"
    _kolom_inhoud = "melding.meta.id"
    _th_standaard_classes = "nowrap"


class AdresKolom(StandaardKolom):
    _key = "adres"
    _kolom_hoofd = "Ter hoogte van"
    _td_standaard_classes = "nowrap"
    _ordering_value = "locaties_voor_melding__straatnaam"

    def td_label(self):
        default = "-"
        locatie_key = "melding.locaties_voor_melding.0"
        if locatie := string_based_lookup(
            self.context, locatie_key, not_found_value={}
        ):
            straatnaam = locatie.get("straatnaam", "")
            huisnummer = locatie.get("huisnummer", "")
            huisletter = locatie.get("huisletter", "")
            toevoeging = locatie.get("toevoeging", "")

            return (
                f"{string.capwords(straatnaam)} {huisnummer}{huisletter} {toevoeging}".strip()
                if straatnaam
                else default
            )

        return default


class AdresBuurtWijkKolom(StandaardKolom):
    _key = "adres_buurt_wijk"
    _kolom_hoofd = "Ter hoogte van"
    _td_standaard_classes = "nowrap"
    _ordering_value = "locaties_voor_melding__straatnaam"

    def td_label(self):
        default = "-"
        locatie_key = "melding.locaties_voor_melding.0"
        if locatie := string_based_lookup(
            self.context, locatie_key, not_found_value={}
        ):
            straatnaam = locatie.get("straatnaam", "")
            huisnummer = (
                f' {locatie.get("huisnummer")}' if locatie.get("huisnummer") else ""
            )
            huisletter = (
                f'{locatie.get("huisletter")}' if locatie.get("huisletter") else ""
            )
            toevoeging = (
                f' {locatie.get("toevoeging")}' if locatie.get("toevoeging") else ""
            )
            wijk = locatie.get("wijknaam", "")
            buurt = locatie.get("buurtnaam", "")

            lijst = []
            if wijk:
                lijst.append(wijk)
            if buurt:
                lijst.append(buurt)

            return (
                f"{string.capwords(straatnaam)}{huisnummer}{huisletter}{toevoeging}<br>{', '.join(lijst)}".strip()
                if straatnaam
                else default
            )


class WijkKolom(StandaardKolom):
    _key = "wijk"
    _kolom_hoofd = "Wijk"
    _kolom_inhoud = "melding.locaties_voor_melding.0.wijknaam"
    _ordering_value = "locaties_voor_melding__wijknaam"
    _td_standaard_classes = "nowrap"


class BuurtKolom(StandaardKolom):
    _key = "buurt"
    _kolom_hoofd = "Buurt"
    _kolom_inhoud = "melding.locaties_voor_melding.0.buurtnaam"
    _ordering_value = "locaties_voor_melding__buurtnaam"
    _td_standaard_classes = "nowrap"


class MeldingIdKolom(StandaardKolom):
    _key = "melding_id"
    _kolom_hoofd = "Melding"
    _kolom_inhoud = "melding.id"
    _ordering_value = "id"

    def td_inhoud(self):
        uuid = string_based_lookup(self.context, "melding.uuid")
        return mark_safe(
            f"<a href='./{uuid}' data-turbo-action='advance' data-turbo-prefetch='false'>{self.td_label()}</a>"
        )


class BegraafplaatsKolom(StandaardKolom):
    _key = "begraafplaats"
    _kolom_hoofd = "Begraafplaats"
    _kolom_inhoud = "melding.locaties_voor_melding.0.begraafplaats"
    _ordering_value = "locaties_voor_melding__begraafplaats"
    _td_standaard_classes = "nowrap"

    def td_label(self):
        default = "-"
        begraafplaats = string_based_lookup(self.context, self._kolom_inhoud)
        begraafplaatsen = (
            self.context.get("data", {}).get("filter_options", {}).get(self._key, {})
        )
        begraafplaats_naam = begraafplaatsen.get(begraafplaats, begraafplaats)
        return begraafplaats_naam[0] if begraafplaats_naam else default


class GrafnummerKolom(StandaardKolom):
    _key = "grafnummer"
    _kolom_hoofd = "Grafnummer"
    _kolom_inhoud = "melding.locaties_voor_melding.0.grafnummer"
    _ordering_value = "locaties_voor_melding__grafnummer"


class VakKolom(StandaardKolom):
    _key = "vak"
    _kolom_hoofd = "Vak"
    _kolom_inhoud = "melding.locaties_voor_melding.0.vak"
    _ordering_value = "locaties_voor_melding__vak"


class OnderwerpKolom(StandaardKolom):
    _key = "onderwerp"
    _kolom_hoofd = "Onderwerp"
    _kolom_inhoud = "melding.onderwerpen"

    def td_label(self):
        default = "-"
        onderwerpen_urls = string_based_lookup(self.context, self._kolom_inhoud)
        if not onderwerpen_urls:
            return default
        onderwerp_namen = [
            render_onderwerp(onderwerp_url) for onderwerp_url in onderwerpen_urls
        ]
        return ", ".join(onderwerp_namen) if onderwerp_namen else default


class OrigineelAangemaaktKolom(StandaardKolom):
    _key = "origineel_aangemaakt"
    _kolom_hoofd = "Datum"
    _kolom_inhoud = "melding.origineel_aangemaakt"
    _ordering_value = "origineel_aangemaakt"
    _td_standaard_classes = "nowrap"

    def td_label(self):
        default = "-"
        origineel_aangemaakt = string_based_lookup(
            self.context, self._kolom_inhoud, not_found_value=""
        )
        if not origineel_aangemaakt:
            return default
        return stringdatetime_naar_datetime(origineel_aangemaakt).strftime(
            "%Y-%m-%d %H:%M"
        )


class StatusKolom(StandaardKolom):
    _key = "status"
    _kolom_hoofd = "Status"
    _kolom_inhoud = "melding.status.naam"
    _ordering_value = "status__naam"
    _td_standaard_classes = "nowrap"

    def td_inhoud(self):
        colors = {
            "afgehandeld": "green",
            "controle": "yellow",
            "in_behandeling": "darkblue",
            "geannuleerd": "red",
        }
        taakopdrachten_voor_melding = [
            taak
            for taak in string_based_lookup(
                self.context, "melding.taakopdrachten_voor_melding", not_found_value=[]
            )
            if taak.get("status", {}).get("naam", "")
            not in ["voltooid", "niet_voltooid"]
        ]

        taakopdrachten_voor_melding = (
            f"({len(taakopdrachten_voor_melding)})"
            if taakopdrachten_voor_melding
            else ""
        )
        status_naam = string_based_lookup(
            self.context, self._kolom_inhoud, not_found_value=""
        )
        return mark_safe(
            f'<span class="display--flex--center badge badge--{colors.get(status_naam, "lightblue")}">{VERTALINGEN.get(status_naam, status_naam)}{taakopdrachten_voor_melding}</span>'
        )


class MeldRNummerKolom(StandaardKolom):
    _key = "meldr_nummer"
    _kolom_hoofd = "MeldR nummer"
    _kolom_inhoud = "melding.meta.meldingsnummerField"
    _ordering_value = "meta__meldingsnummerField"
    _td_standaard_classes = "nowrap"

    def td_label(self):
        bron_signaal_ids = [
            signaal.get("bron_signaal_id", "") if signaal.get("bron_signaal_id") else ""
            for signaal in self.context.get("melding", {}).get(
                "signalen_voor_melding", []
            )
        ]
        meta_meldr_nummer = string_based_lookup(
            self.context, self._kolom_inhoud, not_found_value=""
        )
        msb_meldr_nummer = string_based_lookup(
            self.context, "melding.meta.morId", not_found_value=""
        )
        bron_signaal_ids.append(meta_meldr_nummer)
        bron_signaal_ids.append(msb_meldr_nummer)

        bron_signaal_ids_joined = (
            "<div class='clamped'>"
            + "<br>".join([id for id in bron_signaal_ids if id])
            + "</div>"
        )

        return bron_signaal_ids_joined


class SpoedKolom(StandaardKolom):
    _key = "spoed"
    _kolom_hoofd = "Spoed"
    _kolom_inhoud = "melding.urgentie"
    _ordering_value = "urgentie"

    def td_label(self):
        if self.context.get("melding", {}).get("urgentie", 0) >= 0.5:
            spoed_badge = get_template("badges/spoed.html")
            return spoed_badge.render()
        return ""


class StandaardFilter:
    _key = None
    _group = False
    _label = None

    def __init__(self, context):
        self.context = context

    @classmethod
    def key(cls):
        return cls._key

    @classmethod
    def label(cls):
        return cls._label if cls._label else cls._key

    @classmethod
    def update_filter_querydict(cls, querydict, filter_value):
        querydict.setlist(cls._key, filter_value)
        return querydict

    def optie_label(self, optie_data):
        return f"{VERTALINGEN.get(optie_data[0], optie_data[0])}"

    def opties(self):
        if self._group:
            groups = list(
                set([v[1] for k, v in self.context.items() if len(v) > 1 and v[1]])
            )
            return sorted(
                [
                    [
                        g,
                        sorted(
                            [
                                [
                                    k,
                                    {
                                        "label": self.optie_label(v),
                                        "item_count": v[1],
                                    },
                                ]
                                for k, v in self.context.items()
                                if len(v) > 1 and g == v[1]
                            ],
                            key=lambda b: b[1].get("label"),
                        ),
                    ]
                    for g in groups
                ],
                key=lambda b: b[0],
            )
        return [
            [
                k,
                {
                    "label": self.optie_label(v),
                    "item_count": v[1],
                },
            ]
            for k, v in self.context.items()
        ]


class StatusFilter(StandaardFilter):
    _key = "status"

    def opties(self):
        return [
            ["afgehandeld", {"label": "Afgehandeld"}],
            ["controle", {"label": "Controle"}],
            ["geannuleerd", {"label": "Geannuleerd"}],
            ["pauze", {"label": "Gepauzeerd"}],
            ["in_behandeling", {"label": "In behandeling"}],
            ["openstaand", {"label": "Openstaand"}],
            ["wachten_melder", {"label": "Wachten op melder"}],
        ]


class SpoedFilter(StandaardFilter):
    _key = "urgentie_gte"
    _label = "Spoed"

    @classmethod
    def update_filter_querydict(cls, querydict, filter_value):
        if "spoed" in filter_value and len(filter_value) == 1:
            querydict.setlist("urgentie_gte", [0.5])
        if "geen_spoed" in filter_value and len(filter_value) == 1:
            querydict.setlist("urgentie_lt", [0.5])
        return querydict

    def opties(self):
        return [
            ["spoed", {"label": "Spoed"}],
            ["geen_spoed", {"label": "Geen spoed"}],
        ]


class BegraafplaatsFilter(StandaardFilter):
    _key = "begraafplaats"


class OnderwerpFilter(StandaardFilter):
    _key = "onderwerp"
    _group = True

    def optie_label(self, optie_data):
        if len(optie_data) < 2:
            return optie_data
        return render_onderwerp(optie_data[0], optie_data[1])

    def opties(self):
        if self._group:
            groups = render_onderwerp_groepen(self.context)
            if groups:
                return groups
        opties = [
            [
                k,
                {
                    "label": self.optie_label(v),
                    "item_count": v[1],
                },
            ]
            for k, v in self.context.items()
        ]
        return opties


class WijkFilter(StandaardFilter):
    _key = "wijk"


class BuurtFilter(StandaardFilter):
    _key = "buurt"
    _group = True
    _label = "Wijk en buurt"


FILTERS = (
    StatusFilter,
    BegraafplaatsFilter,
    OnderwerpFilter,
    WijkFilter,
    BuurtFilter,
    SpoedFilter,
)


class FilterManager:
    _valid_filters = FILTERS

    def __init__(self, *args, **kwargs):
        self._filterclass_by_key = {f.key(): f for f in self._valid_filters}

    def _get_class_by_key(self, k):
        return self._filterclass_by_key.get(k)

    def get_query_string(self, query_dict):
        new_query_dict = QueryDict("", mutable=True)
        for k, v in query_dict.items():
            filter_cls = self._get_class_by_key(k)
            if filter_cls:
                filter_cls.update_filter_querydict(
                    new_query_dict, query_dict.getlist(k)
                )
            else:
                new_query_dict.setlist(k, query_dict.getlist(k))
        return new_query_dict.urlencode()


FILTER_KEYS = [f.key() for f in FILTERS]
FILTER_CLASS_BY_KEY = {f.key(): f for f in FILTERS}

KOLOMMEN = (
    MeldingIdKolom,
    MSBNummerKolom,
    MeldRNummerKolom,
    AdresKolom,
    AdresBuurtWijkKolom,
    WijkKolom,
    BuurtKolom,
    BegraafplaatsKolom,
    GrafnummerKolom,
    VakKolom,
    OnderwerpKolom,
    OrigineelAangemaaktKolom,
    StatusKolom,
    SpoedKolom,
)
KOLOM_KEYS = [f.key() for f in KOLOMMEN]
KOLOM_CLASS_BY_KEY = {k.key(): k for k in KOLOMMEN}
