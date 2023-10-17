import string
from utils.datetime import stringdatetime_naar_datetime

from apps.regie.constanten import VERTALINGEN
from apps.services.onderwerpen import OnderwerpenService, render_onderwerp
from django.http import QueryDict
from django.template.loader import get_template
from django.urls import reverse
from django.utils.safestring import mark_safe
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
    _kolom_hoofd = "Adres"
    _td_standaard_classes = "nowrap"
    _ordering_value = "locaties_voor_melding__straatnaam"

    def td_label(self):
        default = "-"
        straatnaam = string_based_lookup(
            self.context,
            "melding.locaties_voor_melding.0.straatnaam",
            not_found_value="",
        )
        huisnummer = string_based_lookup(
            self.context,
            "melding.locaties_voor_melding.0.huisnummer",
            not_found_value="",
        )

        return f"{string.capwords(straatnaam)} {huisnummer}" if straatnaam else default


class AdresBuurtWijkKolom(StandaardKolom):
    _key = "adres_buurt_wijk"
    _kolom_hoofd = "Adres"
    _td_standaard_classes = "nowrap"
    _ordering_value = "locaties_voor_melding__straatnaam"

    def td_label(self):
        default = "-"
        straatnaam = string_based_lookup(
            self.context,
            "melding.locaties_voor_melding.0.straatnaam",
            not_found_value="",
        )
        huisnummer = string_based_lookup(
            self.context,
            "melding.locaties_voor_melding.0.huisnummer",
            not_found_value="",
        )
        buurt = string_based_lookup(
            self.context,
            "melding.locaties_voor_melding.0.buurtnaam",
            not_found_value="",
        )
        wijk = string_based_lookup(
            self.context,
            "melding.locaties_voor_melding.0.wijknaam",
            not_found_value="",
        )

        list = []
        if len(buurt) > 0:
            list.append(buurt)
        if len(wijk) > 0:
            list.append(wijk)

        return (
            f"{string.capwords(straatnaam)} {huisnummer}" + "<br>" + ", ".join(list)
            if list
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
            f"<a href='./{uuid}' data-turbo-action='advance'>{self.td_label()}</a>"
        )


class BegraafplaatsKolom(StandaardKolom):
    _key = "begraafplaats"
    _kolom_hoofd = "Begraafplaats"
    _kolom_inhoud = "melding.locaties_voor_melding.0.begraafplaats"
    _ordering_value = "locaties_voor_melding__begraafplaats"
    _td_standaard_classes = "nowrap"

    def td_label(self):
        default = "-"
        begraafplaats = string_based_lookup(
            self.context, "melding.locaties_voor_melding.0.begraafplaats"
        )
        begraafplaatsen = self.context.get("filter_options", {}).get(
            "begraafplaats", {}
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
    _kolom_inhoud = "melding.locaties_voor_melding.0.vak"

    def td_label(self):
        default = "-"
        onderwerpen_urls = string_based_lookup(self.context, "melding.onderwerpen")
        if not onderwerpen_urls:
            return default
        onderwerp_namen = [render_onderwerp(onderwerp_url) for onderwerp_url in onderwerpen_urls]
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
            self.context, "melding.origineel_aangemaakt", not_found_value=""
        )
        if not origineel_aangemaakt:
            return default
        return stringdatetime_naar_datetime(origineel_aangemaakt).strftime("%Y-%m-%d %H:%M")


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
        }
        aantal_actieve_taken = string_based_lookup(
            self.context, "melding.aantal_actieve_taken", not_found_value=""
        )
        if aantal_actieve_taken:
            aantal_actieve_taken = f"({aantal_actieve_taken})"
        status_naam = string_based_lookup(
            self.context, "melding.status.naam", not_found_value=""
        )
        return mark_safe(
            f'<span class="display--flex--center badge badge--{colors.get(status_naam, "lightblue")}">{VERTALINGEN.get(status_naam, status_naam)}{aantal_actieve_taken}</span>'
        )


class StandaardFilter:
    _key = None

    def __init__(self, context):
        self.context = context

    @classmethod
    def key(cls):
        return cls._key

    def optie_label(self, optie_data):
        return f"{VERTALINGEN.get(optie_data[0], optie_data[0])}"

    def opties(self):
        return [
            [k, {"label": self.optie_label(v), "item_count": v[1]}]
            for k, v in self.context.items()
        ]


class StatusFilter(StandaardFilter):
    _key = "status"


class BegraafplaatsFilter(StandaardFilter):
    _key = "begraafplaats"


class OnderwerpFilter(StandaardFilter):
    _key = "onderwerp"

    def optie_label(self, optie_data):
        if len(optie_data) < 2:
            return optie_data
        return render_onderwerp(optie_data[0], optie_data[1])


class WijkFilter(StandaardFilter):
    _key = "wijk"


class BuurtFilter(StandaardFilter):
    _key = "buurt"


FILTERS = (
    StatusFilter,
    BegraafplaatsFilter,
    OnderwerpFilter,
    WijkFilter,
    BuurtFilter,
)

FILTER_NAMEN = [f.key() for f in FILTERS]
FILTER_KEYS = {f.key(): f for f in FILTERS}

KOLOMMEN = (
    MeldingIdKolom,
    MSBNummerKolom,
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
)
KOLOMMEN_KEYS = {k.key(): k for k in KOLOMMEN}
