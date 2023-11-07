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


@register.simple_tag
def enhance_ordering_options(options):
    return [
        {
            **o,
            "hide": i == 1
            and len([oo for oo in options if not oo.get("selected")]) == 2
            or options[i].get("selected"),
        }
        for i, o in enumerate(options)
    ]


@register.simple_tag
def get_selected_ordering_option(options):
    selected_options = [o for o in options if o.get("selected")]
    return selected_options[0] if selected_options else None
