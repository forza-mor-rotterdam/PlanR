import base64
from re import sub

from django.core.files.storage import default_storage
from django.http import QueryDict


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


def melding_naar_tijdlijn(melding: dict):
    tijdlijn_data = []
    t_ids = []
    row = []
    for mg in reversed(melding.get("meldinggebeurtenissen", [])):
        row = [0 for t in t_ids]

        tg = mg.get("taakgebeurtenis", {}) if mg.get("taakgebeurtenis", {}) else {}
        taakstatus_is_voltooid = (
            tg and tg.get("taakstatus", {}).get("naam") == "voltooid"
        )
        taakstatus_event = tg and tg.get("taakstatus", {}).get("naam") in [
            "toegewezen",
            "openstaand",
        ]
        t_id = tg.get("taakopdracht")
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

        row.insert(0, 0 if tg else 1)

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


def update_qd_met_standaard_meldingen_filter_qd(qd, gebruiker_context=None):
    meldingen_filter_qd = QueryDict("", mutable=True)
    meldingen_filter_qd.update(qd)
    if gebruiker_context:
        for k, v in gebruiker_context.standaard_filters.items():
            for vv in v:
                meldingen_filter_qd.update({k: vv})
    return meldingen_filter_qd


def truncate_tekst(text, length=200):
    if len(text) > length:
        return f"{text[:length]}..."
    return text
