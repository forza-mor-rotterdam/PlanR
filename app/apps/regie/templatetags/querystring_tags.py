from apps.regie.utils import dict_to_querystring
from django import template

register = template.Library()


@register.filter
def qs_ordenen(request_get, orden_param):
    qs_huidige_dict = dict(request_get)
    if orden_param in qs_huidige_dict.get("ordering", []):
        qs_huidige_dict.update({"ordering": [f"-{orden_param}"]})
    else:
        qs_huidige_dict.update({"ordering": [orden_param]})

    return dict_to_querystring(qs_huidige_dict)


@register.filter
def heeft_orden_oplopend(request_get, orden_param):
    qs_huidige_dict = dict(request_get)
    if f"-{orden_param}" in qs_huidige_dict.get("ordering", []):

        return "sorting--down"

    if orden_param in qs_huidige_dict.get("ordering", []):

        return "sorting--up"

    return ""


@register.simple_tag
def vind_in_dict(op_zoek_dict, key):
    if type(op_zoek_dict) != dict:
        return key

    return op_zoek_dict.get(key, key)