from apps.main.utils import dict_to_querystring
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

    # show sorting icon on default
    if len(qs_huidige_dict) == 0 and orden_param == "origineel_aangemaakt":
        return "sorting--down"

    return ""


@register.filter
def qs_offset(request_get, offset_param):
    qs_huidige_dict = dict(request_get)
    qs_huidige_dict.update({"offset": [offset_param]})

    return dict_to_querystring(qs_huidige_dict)


@register.simple_tag
def vind_in_dict(op_zoek_dict, key, default=None):
    if not isinstance(op_zoek_dict, dict):
        return key
    if not default:
        default = key
    result = op_zoek_dict.get(key, op_zoek_dict.get(str(key), default))
    if isinstance(result, (list, tuple)):
        return result[0]
    return result
