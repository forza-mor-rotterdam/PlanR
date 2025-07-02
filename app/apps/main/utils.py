import base64
import logging
from collections import OrderedDict
from datetime import datetime
from re import sub

from apps.main.services import MercureService
from django.core.files.storage import default_storage
from django.http import QueryDict
from django.template.loader import get_template
from utils.case_conversions import to_kebab

logger = logging.getLogger(__name__)


def snake_case(s: str) -> str:
    return "_".join(
        sub(
            "([A-Z][a-z]+)",
            r" \1",
            sub("([A-Z]+)", r" \1", s.replace("-", " ")),
        ).split()
    ).lower()


def dict_to_querystring(d: dict) -> str:
    return "&".join([f"{p}={v}" for p, l in d.items() for v in l])


def querystring_to_dict(s: str) -> dict:
    return dict(QueryDict(s))


def to_base64(file):
    binary_file = default_storage.open(file)
    binary_file_data = binary_file.read()
    base64_encoded_data = base64.b64encode(binary_file_data)
    base64_message = base64_encoded_data.decode("utf-8")
    return base64_message


def melding_locaties(melding: dict):
    locaties_voor_melding = melding.get("locaties_voor_melding", [])
    signalen_voor_melding = melding.get("signalen_voor_melding", [])
    adressen = [
        locatie
        for locatie in locaties_voor_melding
        if locatie.get("locatie_type") == "adres"
    ]
    lichtmasten = [
        locatie
        | {
            "bron_id": signaal.get("bron_id"),
            "bron_signaal_id": signaal.get("bron_signaal_id"),
        }
        for signaal in signalen_voor_melding
        for locatie in signaal.get("locaties_voor_signaal", [])
        if locatie.get("locatie_type") == "lichtmast"
    ]
    lichtmast_ids = sorted(
        list(set([lichtmast.get("lichtmast_id") for lichtmast in lichtmasten]))
    )
    lichtmasten = [
        {
            "lichtmast_id": lichtmast_id,
        }
        | {
            "bron_signaal_ids": [
                lichtmast.get("bron_signaal_id")
                for lichtmast in lichtmasten
                if lichtmast.get("lichtmast_id") == lichtmast_id
            ]
        }
        for lichtmast_id in lichtmast_ids
    ]
    graven = [
        locatie
        for locatie in locaties_voor_melding
        if locatie.get("locatie_type") == "graf"
    ]

    return OrderedDict(
        [
            ("lichtmasten", lichtmasten),
            ("graven", graven),
            (
                "adressen",
                sorted(
                    sorted(adressen, key=lambda b: b.get("gewicht"), reverse=True),
                    key=lambda b: b.get("primair"),
                    reverse=True,
                ),
            ),
        ]
    )


def melding_naar_tijdlijn(melding: dict):
    tijdlijn_data = []
    t_ids = []
    row = []
    for mg in reversed(melding.get("meldinggebeurtenissen", [])):
        row = [0 for t in t_ids]

        taakgebeurtenis = (
            mg.get("taakgebeurtenis", {}) if mg.get("taakgebeurtenis", {}) else {}
        )
        taakstatus_is_voltooid = (
            taakgebeurtenis
            and taakgebeurtenis.get("taakstatus")
            and taakgebeurtenis.get("taakstatus", {}).get("naam")
            in {"voltooid", "voltooid_met_feedback"}
        ) or taakgebeurtenis.get("verwijderd_op")
        taakstatus_event = (
            taakgebeurtenis
            and taakgebeurtenis.get("taakstatus")
            and taakgebeurtenis.get("taakstatus", {}).get("naam")
            in [
                "toegewezen",
                "openstaand",
            ]
            or taakgebeurtenis
            and taakgebeurtenis.get("gebeurtenis_type") == "gedeeld"
        )
        t_id = taakgebeurtenis.get("taakopdracht")
        if t_id and t_id not in t_ids:
            try:
                i = t_ids.index(-1)
                t_ids[i] = t_id
                row[i] = 1
            except Exception:
                t_ids.append(t_id)
                row.append(1)

        if taakstatus_is_voltooid:
            index = t_ids.index(t_id)
            row[index] = 2
        if taakstatus_event:
            index = t_ids.index(t_id)
            row[index] = 3
        for i, t in enumerate(t_ids):
            row[i] = -1 if t == -1 else row[i]

        row.insert(0, 0 if taakgebeurtenis else 1)

        if taakstatus_is_voltooid:
            index = t_ids.index(t_id)
            if index + 1 >= len(t_ids):
                del t_ids[-1]
            else:
                t_ids[index] = -1

        row_dict = {
            "mg": mg,
            "row": row,
        }
        tijdlijn_data.append(row_dict)

    row_dict = {
        "row": [t if t not in [1, 2, 3] else 0 for t in row],
    }
    tijdlijn_data.append(row_dict)
    tijdlijn_data = [t for t in reversed(tijdlijn_data)]
    return tijdlijn_data


def is_valid_callable(key):
    return key is not None and callable(key)


def get_valide_kolom_classes(gebruiker_context):
    from apps.context.constanten import KOLOM_CLASS_BY_KEY

    return [
        KOLOM_CLASS_BY_KEY.get(k)
        for k in gebruiker_context.kolommen.get("sorted", [])
        if KOLOM_CLASS_BY_KEY.get(k)
        if is_valid_callable(KOLOM_CLASS_BY_KEY.get(k))
    ]


def get_valide_filter_classes(gebruiker_context):
    from apps.context.constanten import FILTER_CLASS_BY_KEY

    return [
        FILTER_CLASS_BY_KEY.get(f)
        for f in gebruiker_context.filters.get("fields", [])
        if FILTER_CLASS_BY_KEY.get(f)
        if is_valid_callable(FILTER_CLASS_BY_KEY.get(f))
    ]


def update_qd_met_standaard_meldingen_filter_qd(qd, gebruiker_context=None):
    meldingen_filter_qd = QueryDict("", mutable=True)
    if gebruiker_context:
        for k, v in gebruiker_context.standaard_filters.items():
            if k == "pre_onderwerp":
                continue
            if isinstance(v, (list, tuple)):
                for vv in v:
                    meldingen_filter_qd.update({k: vv})
            else:
                meldingen_filter_qd.update({k: v})
    meldingen_filter_qd.update(qd)
    if not qd.get("search_with_profiel_context"):
        for f in gebruiker_context.filters.get("fields", []):
            if meldingen_filter_qd.get(f):
                del meldingen_filter_qd[f]
    return meldingen_filter_qd


def truncate_tekst(text, length=200):
    if len(text) > length:
        return f"{text[:length]}..."
    return text


def get_actieve_filters(gebruiker):
    if not hasattr(gebruiker, "profiel") or not hasattr(gebruiker.profiel, "context"):
        return {}
    return {
        k: gebruiker.profiel.filters.get(k, [])
        for k in gebruiker.profiel.context.filters.get("fields", [])
    }


def set_actieve_filters(gebruiker, actieve_filters, save=True):
    import copy

    filters = copy.deepcopy(gebruiker.profiel.filters)
    available_fields = gebruiker.profiel.context.filters.get("fields", [])
    actieve_filters = {k: actieve_filters.get(k, []) for k in available_fields}
    filters.update(actieve_filters)
    unused_keys = [k for k, v in filters.items() if k not in available_fields]
    for k in unused_keys:
        filters.pop(k, None)
    if save:
        gebruiker.profiel.filters = filters
        gebruiker.profiel.save()
    return filters


def get_ui_instellingen(gebruiker):
    return {
        "ordering": gebruiker.profiel.ui_instellingen.get(
            "ordering", "-origineel_aangemaakt"
        ),
        "search_with_profiel_context": gebruiker.profiel.ui_instellingen.get(
            "search_with_profiel_context", "on"
        ),
    }


def set_ui_instellingen(gebruiker, nieuwe_ordering, search_with_profiel_context):
    ui_instellingen = {
        "ordering": nieuwe_ordering,
        "search_with_profiel_context": search_with_profiel_context,
    }
    gebruiker.profiel.ui_instellingen.update(ui_instellingen)
    gebruiker.profiel.save()
    ui_instellingen.update({"search_with_profiel_context": search_with_profiel_context})
    return ui_instellingen


def subscriptions_voor_topic(topic, alle_subscriptions):
    subscriptions = [
        subscription
        for subscription in alle_subscriptions
        if subscription.get("topic") == topic
    ]
    out = [
        v
        for k, v in {
            subscription.get("payload", {})
            .get("gebruiker", {})
            .get("email"): subscription
            for subscription in subscriptions
        }.items()
    ]
    return out


def publiceer_topic_met_subscriptions(topic, alle_subscriptions=None):
    mercure_service = None
    try:
        mercure_service = MercureService()
    except MercureService.ConfigException:
        return "MercureService.ConfigException error"
    if not alle_subscriptions:
        alle_subscriptions = mercure_service.get_subscriptions().get(
            "subscriptions", []
        )
    subscriptions = subscriptions_voor_topic(topic, alle_subscriptions)
    mercure_service.publish(topic, subscriptions)


def taak_status_tekst(taak, css_class=False):
    # MOR-Core taakopdracht statussen/resoluties
    NIEUW = "nieuw"
    VOLTOOID = "voltooid"
    VOLTOOID_MET_FEEDBACK = "voltooid_met_feedback"
    OPGELOST = "opgelost"
    NIET_OPGELOST = "niet_opgelost"
    GEANNULEERD = "geannuleerd"
    NIET_GEVONDEN = "niet_gevonden"
    voltooid_statussen = [VOLTOOID, VOLTOOID_MET_FEEDBACK]

    # vertalingen van MOR-Core taakopdracht statussen
    taak_statussen = {
        NIEUW: "Openstaand",
        VOLTOOID: "Voltooid",
        VOLTOOID_MET_FEEDBACK: "Voltooid met feedback",
    }
    # vertalingen van MOR-Core taakopdracht resoluties
    taak_resoluties = {
        OPGELOST: "Voltooid",
        NIET_OPGELOST: "Niet opgelost",
        GEANNULEERD: "Geannuleerd",
        NIET_GEVONDEN: "Niets aangetroffen",
    }
    huidige_status_naam = taak.get("status", {}).get("naam")

    if taak["verwijderd_op"]:
        return "Verwijderd" if not css_class else "verwijderd"

    if huidige_status_naam in voltooid_statussen:
        return (
            taak_resoluties.get(taak["resolutie"], taak.get("resolutie", NIET_OPGELOST))
            if not css_class
            else to_kebab(taak.get("resolutie", NIET_OPGELOST))
        )
    return (
        taak_statussen.get(huidige_status_naam, huidige_status_naam)
        if not css_class
        else to_kebab(huidige_status_naam)
    )


def melding_taken(melding):
    taakopdrachten_voor_melding = [
        taakopdracht for taakopdracht in melding.get("taakopdrachten_voor_melding", [])
    ]
    niet_verwijderde_taken = [
        taak for taak in taakopdrachten_voor_melding if not taak["verwijderd_op"]
    ]
    actieve_taken = [
        taakopdracht
        for taakopdracht in taakopdrachten_voor_melding
        if taakopdracht.get("status", {}).get("naam")
        not in {"voltooid", "voltooid_met_feedback"}
        and not taakopdracht.get("verwijderd_op")
    ]
    open_taken = [
        taakopdracht
        for taakopdracht in taakopdrachten_voor_melding
        if not taakopdracht.get("resolutie") and not taakopdracht.get("verwijderd_op")
    ]
    opgeloste_taken = [
        taakopdracht
        for taakopdracht in taakopdrachten_voor_melding
        if taakopdracht.get("resolutie") == "opgelost"
    ]
    niet_opgeloste_taken = [
        taakopdracht
        for taakopdracht in taakopdrachten_voor_melding
        if taakopdracht.get("resolutie") in ("niet_opgelost",)
    ]

    aantal_actieve_taken = len(actieve_taken)

    return {
        "alle_taken": taakopdrachten_voor_melding,
        "niet_verwijderde_taken": niet_verwijderde_taken,
        "actieve_taken": actieve_taken,
        "open_taken": open_taken,
        "aantal_actieve_taken": aantal_actieve_taken,
        "niet_opgeloste_taken": niet_opgeloste_taken,
        "opgeloste_taken": opgeloste_taken,
    }


class LogboekItem:
    MELDING_AANGEMAAKT = "melding_aangemaakt"
    MELDING_GEANNULEERD = "melding_geannuleerd"
    MELDING_HEROPEND = "melding_heropend"
    MELDING_AFGEHANDELD = "melding_afgehandeld"
    MELDING_GEPAUZEERD = "melding_gepauzeerd"
    MELDING_HERVAT = "melding_hervat"
    AFBEELDING_TOEGEVOEGD = "afbeelding_toegevoegd"
    NOTITIE_TOEGEVOEGD = "notitie_toegevoegd"
    LOCATIE_AANGEMAAKT = "locatie_aangemaakt"
    URGENTIE_AANGEPAST = "urgentie_aangepast"
    SIGNAAL_TOEGEVOEGD = "signaal_toegevoegd"
    TAAK_AANGEMAAKT = "taak_aangemaakt"
    TAAK_AFGEHANDELD = "taak_afgehandeld"
    TAAK_VERWIJDERD = "taak_verwijderd"

    _types = {
        MELDING_AANGEMAAKT: "Melding aangemaakt",
        MELDING_GEANNULEERD: "Melding geannuleerd",  # check mor-core
        MELDING_HEROPEND: "Melding heropend",
        MELDING_AFGEHANDELD: "Melding afgehandeld",
        MELDING_GEPAUZEERD: "Melding gepauzeerd",  # check mor-core
        MELDING_HERVAT: "Melding hervat",  # check mor-core
        AFBEELDING_TOEGEVOEGD: "Afbeelding toegevoegd",
        NOTITIE_TOEGEVOEGD: "Notitie toegevoegd",
        LOCATIE_AANGEMAAKT: "Locatie aangepast",
        URGENTIE_AANGEPAST: "Spoed aangepast",
        SIGNAAL_TOEGEVOEGD: "Melding ontdubbeld",
        TAAK_AANGEMAAKT: 'Taak "%(titel)s" aangemaakt',
        TAAK_AFGEHANDELD: 'Taak "%(titel)s" afgehandeld',
        TAAK_VERWIJDERD: 'Taak "%(titel)s" verwijderd',
    }
    _type = None

    def __init__(
        self,
        meldinggebeurtenis,
        taakopdrachten,
        vorige_meldinggebeurtenis=None,
        signalen=[],
    ):
        self._meldinggebeurtenis = meldinggebeurtenis
        self._signaal_via_href = {
            signaal["_links"]["self"]: signaal for signaal in signalen
        }
        self._vorige_meldinggebeurtenis = vorige_meldinggebeurtenis
        self._taakopdrachten_via_id = {
            taakopdracht["id"]: taakopdracht for taakopdracht in taakopdrachten
        }
        self._resolutie = meldinggebeurtenis.get("resolutie")
        self._bijlagen = meldinggebeurtenis["bijlagen"]
        self._locatie = meldinggebeurtenis["locatie"]
        self._urgentie = meldinggebeurtenis["urgentie"]
        self._signaal = meldinggebeurtenis.get("signaal")
        self._gebeurtenis_type = meldinggebeurtenis["gebeurtenis_type"]
        self._taakgebeurtenis = meldinggebeurtenis["taakgebeurtenis"]

        self._type = self._set_gebeurtenis_type()

    def _set_gebeurtenis_type(self):
        if not self._vorige_meldinggebeurtenis:
            return self.MELDING_AANGEMAAKT
        if self._resolutie:
            return self.MELDING_AFGEHANDELD
        if self._bijlagen:
            return self.AFBEELDING_TOEGEVOEGD
        if self._urgentie:
            return self.URGENTIE_AANGEPAST
        if self._locatie:
            return self.LOCATIE_AANGEMAAKT
        if self._signaal:
            return self.SIGNAAL_TOEGEVOEGD
        if self._gebeurtenis_type == self.MELDING_HEROPEND:
            return self.MELDING_HEROPEND
        if self._taakgebeurtenis:
            self._get_taakopdracht(self._taakgebeurtenis["taakopdracht"])
            if self._taakgebeurtenis["resolutie"]:
                return self.TAAK_AFGEHANDELD
            if self._taakgebeurtenis["verwijderd_op"]:
                return self.TAAK_VERWIJDERD
            return self.TAAK_AANGEMAAKT
        return

    def _get_taakopdracht(self, taakopdracht_id):
        return self._taakopdrachten_via_id.get(
            taakopdracht_id,
            {
                "titel": "-",
                "resolutie": None,
                "verwijderd_op": None,
            },
        )

    @property
    def datumtijd(self):
        return datetime.fromisoformat(self._meldinggebeurtenis["aangemaakt_op"])

    @property
    def datum(self):
        return self.datumtijd.date()

    @property
    def tijd(self):
        return self.datumtijd.strftime("%H:%M")

    @property
    def gebruiker(self):
        o = self._meldinggebeurtenis
        if self._taakgebeurtenis:
            o = self._taakgebeurtenis
        return o.get("gebruiker")

    @property
    def titel(self):
        if self._taakgebeurtenis:
            taakopdracht = self._get_taakopdracht(self._taakgebeurtenis["taakopdracht"])
            return self._types[self._type] % taakopdracht
        return self._types.get(self._type, "Onbekend logboek item")

    @property
    def omschrijving_intern(self):
        o = self._meldinggebeurtenis
        if self._taakgebeurtenis:
            o = self._taakgebeurtenis
        return o.get("omschrijving_intern")

    @property
    def omschrijving_extern(self):
        o = self._meldinggebeurtenis
        if self._taakgebeurtenis:
            o = self._taakgebeurtenis
        return o.get("omschrijving_extern")

    @property
    def bijlagen(self):
        o = self._meldinggebeurtenis
        signaal_href = self._meldinggebeurtenis["_links"]["signaal"]["href"]
        if signaal_href:
            o = self._signaal_via_href.get(signaal_href, {})
        if self._taakgebeurtenis:
            o = self._taakgebeurtenis
        return o.get("bijlagen")

    @property
    def icon(self):
        return f"logboek/icons/{self._type}.svg"

    @property
    def icon_template(self):
        try:
            return get_template(f"logboek/icons/{self._type}.svg")
        except Exception:
            return get_template("logboek/icons/onbekend.svg")

    @property
    def _content_template(self):
        try:
            return get_template(f"logboek/content/{self._type}.html")
        except Exception:
            return get_template("logboek/content/standaard.html")

    @property
    def render_icon(self):
        return self.icon_template.render()

    @property
    def render_content(self):
        content_context_properties = (
            "titel",
            "icon",
            "gebruiker",
            "tijd",
            "datumtijd",
            "datum",
            "omschrijving_intern",
            "omschrijving_extern",
            "bijlagen",
        )
        return self._content_template.render(
            {
                prop: getattr(self, prop, "not found")
                for prop in content_context_properties
            }
        )


class Logboek:
    def __init__(self, melding):
        meldinggebeurtenissen = melding["meldinggebeurtenissen"]
        taakopdrachten_voor_melding = melding["taakopdrachten_voor_melding"]
        signalen_voor_melding = melding["signalen_voor_melding"]

        meldinggebeurtenissen_sorted = sorted(
            meldinggebeurtenissen, key=lambda x: x["aangemaakt_op"], reverse=False
        )

        logboek_items = [
            LogboekItem(
                meldinggebeurtenis,
                taakopdrachten_voor_melding,
                meldinggebeurtenissen_sorted[i - 1] if i != 0 else None,
                signalen=signalen_voor_melding,
            )
            for i, meldinggebeurtenis in enumerate(meldinggebeurtenissen_sorted)
        ]
        self.logboek_items_gesorteerd = sorted(
            logboek_items, key=lambda x: x.datum, reverse=True
        )

        dagen = sorted(
            list(set([logboek_item.datum for logboek_item in logboek_items])),
            reverse=True,
        )

        self.logboek_items_gegroepeerd = [
            {
                "datum": dag,
                "logboek_items": sorted(
                    [
                        logboek_item
                        for logboek_item in self.logboek_items_gesorteerd
                        if logboek_item.datum == dag
                    ],
                    key=lambda x: x.datum,
                    reverse=True,
                ),
            }
            for dag in dagen
        ]
