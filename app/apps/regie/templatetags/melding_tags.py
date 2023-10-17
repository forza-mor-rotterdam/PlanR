from apps.services.onderwerpen import render_onderwerp as render_onderwerp_service
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def taakopdracht(melding, taakopdracht_id):
    taakopdracht = {
        to.get("id"): to for to in melding.get("taakopdrachten_voor_melding", [])
    }.get(taakopdracht_id, {})
    return taakopdracht


@register.simple_tag(takes_context=True)
def render_th_tags(context, kolommen):
    return mark_safe("\n".join([k(context).th for k in kolommen]))


@register.simple_tag(takes_context=True)
def render_td_tags(context, kolommen):
    return mark_safe("\n".join([k(context).td for k in kolommen]))


@register.simple_tag
def render_onderwerp(onderwerp_url):
    return render_onderwerp_service(onderwerp_url)
