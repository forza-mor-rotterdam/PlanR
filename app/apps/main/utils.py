import base64
import logging
from collections import OrderedDict
from re import sub

from apps.main.services import MercureService
from django.core.files.storage import default_storage
from django.http import QueryDict

logger = logging.getLogger(__name__)


def snake_case(s: str) -> str:
    return "_".join(
        sub(
            "([A-Z][a-z]+)",
            r" \1",
            sub("([A-Z]+)", r" \1", s.replace("-", " ")),
        ).split()
    ).lower()


def get_open_taakopdrachten(melding):
    return [
        to
        for to in melding.get("taakopdrachten_voor_melding", [])
        if not to.get("resolutie")
    ]


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
    adressen = [
        locatie
        for locatie in locaties_voor_melding
        if locatie.get("locatie_type") == "adres"
    ]
    lichtmasten = [
        locatie
        for locatie in locaties_voor_melding
        if locatie.get("locatie_type") == "lichtmast"
    ]
    graven = [
        locatie
        for locatie in locaties_voor_melding
        if locatie.get("locatie_type") == "graf"
    ]

    return OrderedDict(
        [
            (
                "adressen",
                sorted(adressen, key=lambda b: b.get("gewicht"), reverse=True),
            ),
            ("lichtmasten", lichtmasten),
            ("graven", graven),
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
        )
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
            if isinstance(v, (list, tuple)):
                for vv in v:
                    meldingen_filter_qd.update({k: vv})
            else:
                meldingen_filter_qd.update({k: v})
    meldingen_filter_qd.update(qd)
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


def set_actieve_filters(gebruiker, actieve_filters):
    actieve_filters = {
        k: actieve_filters.get(k, [])
        for k in gebruiker.profiel.context.filters.get("fields", [])
    }
    gebruiker.profiel.filters.update(actieve_filters)
    unused_keys = [
        k
        for k, v in gebruiker.profiel.filters.items()
        if k not in gebruiker.profiel.context.filters.get("fields", [])
    ]
    for k in unused_keys:
        gebruiker.profiel.filters.pop(k, None)
    gebruiker.profiel.save()
    return gebruiker.profiel.filters


def get_ordering(gebruiker):
    return gebruiker.profiel.ui_instellingen.get("ordering", "-origineel_aangemaakt")


def set_ordering(gebruiker, nieuwe_ordering):
    gebruiker.profiel.ui_instellingen.update({"ordering": nieuwe_ordering})
    gebruiker.profiel.save()
    return gebruiker.profiel.ui_instellingen.get("ordering")


def subscriptions_voor_topic(topic, alle_subscriptions):
    subscriptions = [
        subscription
        for subscription in alle_subscriptions
        if subscription.get("topic") == topic
    ]
    return [
        v
        for k, v in {
            subscription.get("payload", {})
            .get("gebruiker", {})
            .get("email"): subscription
            for subscription in subscriptions
        }.items()
    ]


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
