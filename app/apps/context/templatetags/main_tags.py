import json
from datetime import datetime

from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def slice_iterable(input, start_int=None, end_int=None):
    try:
        iter(input)
    except TypeError:
        return input
    if start_int is not None and not isinstance(start_int, int):
        return input
    if end_int is not None and not isinstance(end_int, int):
        return input
    if not start_int and not end_int:
        return input
    if start_int is None:
        return input[:end_int]
    if end_int is None:
        return input[start_int:]
    return input[start_int:end_int]


@register.filter
def laatste_slug_van_url(url):
    if not url:
        return url
    qs_removed_from_url = url.split("?")[0]
    stripped_url = qs_removed_from_url.strip("/")
    last_part_from_url = stripped_url.split("/")[-1]
    return last_part_from_url


@register.filter
def mor_core_url(initial_url):
    return f"{settings.MOR_CORE_URL_PREFIX}{initial_url}"


@register.filter
def json_encode(value):
    return json.dumps(value)


@register.filter
def replace_n(value):
    return value.replace("\\n", "<br/>").replace("?", "?<br/>")


@register.simple_tag
def vind_in_dict(op_zoek_dict, key):
    if not isinstance(op_zoek_dict, dict):
        return key
    result = op_zoek_dict.get(key, op_zoek_dict.get(str(key), key))
    if isinstance(result, (list, tuple)):
        return result[0]
    return result


@register.filter
def to_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z")
    except Exception as e:
        print(e)
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z")
    except Exception as e:
        print(e)
    return value


@register.filter
def to_timestamp(value):
    try:
        return int(value.timestamp())
    except Exception:
        print("No datatime instance")


@register.filter(name="python_any")
def python_any(values):
    if values:
        return any(values)
    return values
