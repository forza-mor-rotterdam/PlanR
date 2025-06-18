import base64
import logging
from collections import OrderedDict
from re import sub

from apps.main.services import MercureService
from django.core.files.storage import default_storage
from django.http import QueryDict
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
        for taakopdracht in melding.get("taakopdrachten_voor_melding", [])
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
