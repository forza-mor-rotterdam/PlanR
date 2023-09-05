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


def string_based_lookup(local_vars, lookup_str, seperator=".", not_found_value="-"):
    lookup_list = lookup_str.split(seperator)

    def get_next(i, v):
        if len(lookup_list) == i:
            return v
        try:
            is_int = False
            try:
                int(lookup_list[i])
                is_int = True
            except Exception:
                ...
            if is_int:
                o = v[int(lookup_list[i])]
            else:
                o = v.get(lookup_list[i])
            j = i + 1
            return get_next(j, o)
        except Exception:
            ...

    result = get_next(0, local_vars)
    if not result:
        return not_found_value
    return result
