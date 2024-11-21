from django.template import RequestContext


def absolute(request):
    urls = {
        "ABSOLUTE_ROOT": request.build_absolute_uri("/")[:-1].strip("/"),
        "FULL_URL_WITH_QUERY_STRING": request.build_absolute_uri(),
        "FULL_URL": request.build_absolute_uri("?"),
    }

    return urls


def gebruikersnaam(gebruiker, no_fallback=False):
    if isinstance(gebruiker, dict):
        first_name = gebruiker.get("first_name", "")
        last_name = gebruiker.get("last_name", "")
        full_name = f"{first_name} {last_name}".strip()
        return full_name or (gebruiker.get("email", "") if not no_fallback else "")
    elif hasattr(gebruiker, "first_name") or hasattr(gebruiker, "last_name"):
        first_name = gebruiker.first_name if gebruiker.first_name else ""
        last_name = gebruiker.last_name if gebruiker.last_name else ""
        full_name = f"{first_name} {last_name}".strip()
        return full_name or (gebruiker.email if not no_fallback else "")
    return ""


def gebruikersinitialen(gebruiker):
    if isinstance(gebruiker, dict):
        first_name_initial = gebruiker.get("first_name", "*")[0]
        last_name_initial = gebruiker.get("last_name", "*")[0]
        full_initials = f"{first_name_initial} {last_name_initial}".strip()
    elif hasattr(gebruiker, "first_name") or hasattr(gebruiker, "last_name"):
        first_name_initial = gebruiker.first_name[0] if gebruiker.first_name else "*"
        last_name_initial = gebruiker.last_name[0] if gebruiker.last_name else "*"
        full_initials = f"{first_name_initial}{last_name_initial}".strip()
    return full_initials


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


def get_index(lookup_list: (list | tuple), lookup_value):
    try:
        return lookup_list.index(lookup_value)
    except ValueError:
        return -1
