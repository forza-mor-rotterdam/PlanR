from django import template
from utils.diversen import string_based_lookup

register = template.Library()


@register.filter
def taakopdracht(melding, taakopdracht_id):
    taakopdracht = {
        to.get("id"): to for to in melding.get("taakopdrachten_voor_melding", [])
    }.get(taakopdracht_id, {})
    return taakopdracht


@register.simple_tag(takes_context=True)
def kolom_hoofd(context, kolom_data):
    return kolom_data[1]


@register.simple_tag(takes_context=True)
def kolom_inhoud(context, kolom_data, lookup_object):
    lookup_str = kolom_data[2]
    result = string_based_lookup(
        locals().get("context", {}), lookup_str=lookup_str, not_found_value="n.v.t"
    )
    return result
