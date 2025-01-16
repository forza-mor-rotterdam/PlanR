from apps.main.services import render_onderwerp as render_onderwerp_service
from apps.main.utils import melding_naar_tijdlijn as base_melding_naar_tijdlijn
from apps.main.utils import melding_taken as base_melding_taken
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def taakopdracht(melding, taakopdracht_id):
    taakopdracht = {
        taakopdracht.get("id"): taakopdracht
        for taakopdracht in melding.get("taakopdrachten_voor_melding", [])
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


@register.simple_tag
def get_bijlagen(melding):
    melding_bijlagen = [
        {
            **bijlage,
            "aangemaakt_op": melding.get("aangemaakt_op"),
            "label": "Foto van melder",
        }
        for bijlage in melding.get("bijlagen", [])
    ]
    signaal_bijlagen = [
        {
            **bijlage,
            "signaal": signaal,
            "aangemaakt_op": signaal.get("aangemaakt_op"),
            "label": f"Foto van melder({signaal.get('bron_id')}): {signaal.get('bron_signaal_id')}",
        }
        for signaal in melding.get("signalen_voor_melding", [])
        for bijlage in signaal.get("bijlagen", [])
    ]
    meldinggebeurtenis_bijlagen = [
        {
            **bijlage,
            "meldinggebeurtenis": meldinggebeurtenis,
            "aangemaakt_op": meldinggebeurtenis.get("aangemaakt_op"),
            "label": "Foto van medewerker",
        }
        for meldinggebeurtenis in melding.get("meldinggebeurtenissen", [])
        for bijlage in meldinggebeurtenis.get("bijlagen", [])
    ]
    taakgebeurtenis_bijlagen = [
        {
            **bijlage,
            "taakgebeurtenis": meldinggebeurtenis.get("taakgebeurtenis", {}),
            "aangemaakt_op": meldinggebeurtenis.get("taakgebeurtenis", {}).get(
                "aangemaakt_op"
            ),
            "label": "Foto van medewerker",
        }
        for meldinggebeurtenis in melding.get("meldinggebeurtenissen", [])
        for bijlage in (
            meldinggebeurtenis.get("taakgebeurtenis", {}).get("bijlagen", [])
            if meldinggebeurtenis.get("taakgebeurtenis")
            else []
        )
    ]
    alle_bijlagen = (
        signaal_bijlagen
        + meldinggebeurtenis_bijlagen
        + taakgebeurtenis_bijlagen
        + melding_bijlagen
    )
    alle_bijlagen_gesorteerd = sorted(
        alle_bijlagen, key=lambda b: b.get("aangemaakt_op")
    )
    return alle_bijlagen_gesorteerd


@register.simple_tag
def melding_taken(melding):
    return base_melding_taken(melding)


@register.simple_tag
def melding_naar_tijdlijn(melding):
    return base_melding_naar_tijdlijn(melding)
