from django.template import RequestContext


def absolute(request):
    urls = {
        "ABSOLUTE_ROOT": request.build_absolute_uri("/")[:-1].strip("/"),
        "FULL_URL_WITH_QUERY_STRING": request.build_absolute_uri(),
        "FULL_URL": request.build_absolute_uri("?"),
    }

    return urls


def gebruikersnaam(gebruiker):
    if gebruiker.first_name or gebruiker.last_name:
        first_name = gebruiker.first_name if gebruiker.first_name else ""
        last_name = gebruiker.last_name if gebruiker.last_name else ""
        return f"{first_name} {last_name}".strip()
    return gebruiker.email


def string_based_lookup(local_vars, lookup_str, separator=".", not_found_value="-"):
    lookup_list = lookup_str.split(separator)

    def get_value(keys, data):
        if not keys:
            return data
        key = keys.pop(0)
        if key.isdigit():
            key = int(key)
        if isinstance(data, list) and isinstance(key, int) and 0 <= key < len(data):
            return get_value(keys, data[key])
        elif isinstance(data, (dict, RequestContext)) and key in data:
            return get_value(keys, data[key])
        else:
            raise ValueError(f"Key not found: {key}")

    try:
        result = get_value(lookup_list, local_vars)
    except ValueError:
        result = not_found_value

    return result if result else not_found_value


def get_max_gewicht_locatie(context, locaties_key="melding.locaties_voor_melding"):
    if locaties := string_based_lookup(context, locaties_key, not_found_value=[]):
        if max_locatie := max(
            locaties, key=lambda locatie: locatie.get("gewicht", 0), default=None
        ):
            return max_locatie

    return {}
