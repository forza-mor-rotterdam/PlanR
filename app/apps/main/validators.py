import json
from graphlib import CycleError, TopologicalSorter
from json.decoder import JSONDecodeError

from django.core.exceptions import ValidationError


def validate_taakvolgorde(cleaned_data):
    try:
        taken = [
            taak | {"parents": json.loads(taak["parents"])}
            for taak in cleaned_data
        ]
    except JSONDecodeError:
        raise ValidationError("de parent waarde van een taak bevat geen json")

    taak_ids = {taak["uuid"] for taak in taken}
    if len(taak_ids) != len(taken):
        raise ValidationError("taak id's zijn niet uniek")

    for taak in taken:
        if len(taak["parents"]) != len(set(taak["parents"])):
            raise ValidationError(
                f"meerdere identieke relatie gevonden: {taak['uuid']}"
            )
        if taak["uuid"] in taak["parents"]:
            raise ValidationError(
                f"taak verwijst naar zichzelf: {taak['uuid']} in {json.dumps(taak['parents'])}"
            )

    # Use TopologicalSorter for cycle detection (only consider in-batch parents)
    graph = {
        taak["uuid"]: [p for p in taak["parents"] if p in taak_ids]
        for taak in taken
    }
    try:
        TopologicalSorter(graph).prepare()
    except CycleError:
        raise ValidationError("taak volgorde bevat een circulaire afhankelijkheid")

    return taken
