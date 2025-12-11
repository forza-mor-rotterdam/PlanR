import json
from json.decoder import JSONDecodeError

from django.core.exceptions import ValidationError


def validate_taakvolgorde(cleaned_data):
    parents_key = "parents"
    childred_key = "childred"
    id_key = "uuid"
    try:
        taken = [
            taak
            | {
                parents_key: json.loads(taak[parents_key]),
            }
            for taak in cleaned_data
        ]
    except JSONDecodeError:
        raise ValidationError("de parent waarde van een taak bevat geen json")

    taak_ids = [taak[id_key] for taak in taken]
    if len(taak_ids) != len(list(set(taak_ids))):
        raise ValidationError("taak id's zijn niet uniek")

    taken = [
        taak
        | {childred_key: [t[id_key] for t in taken if taak[id_key] in t[parents_key]]}
        for taak in taken
    ]
    for taak in taken:
        if len(taak[parents_key]) != len(list(set(taak[parents_key]))):
            raise ValidationError(
                f"meerdere identieke relatie gevonden: {taak[id_key]}"
            )
        if taak[id_key] in taak[parents_key]:
            raise ValidationError(
                f"taak verwijst naar zichzelf: {taak[id_key]} in {json.dumps(taak[parents_key])}"
            )
        if taak[id_key] in taak[childred_key]:
            raise ValidationError(
                f"taak verwijst naar zichzelf: {taak[id_key]} in {taak[childred_key]}"
            )

    for taak in taken:

        def set_all_related(related_taak, relation):
            uuids = related_taak[relation]
            taak[f"all_{relation}"] = taak.get(f"all_{relation}", []) + uuids
            for uuid in uuids:
                t = [tt for tt in taken if tt[id_key] == uuid]
                if t:
                    set_all_related(t[0], relation)

        try:
            set_all_related(taak, childred_key)
        except Exception:
            raise ValidationError("taak komt voor in 1 of meer van z'n kinderen")

        try:
            set_all_related(taak, parents_key)
        except Exception:
            raise ValidationError("taak komt voor in 1 of meer van z'n ouders")

    for taak in taken:
        if len(taak[f"all_{parents_key}"]) != len(
            list(set(taak[f"all_{parents_key}"]))
        ):
            raise ValidationError(
                f"relatie gevonden die een overeenkomstige ouder hebben: {taak[id_key]}"
            )

    return taken
