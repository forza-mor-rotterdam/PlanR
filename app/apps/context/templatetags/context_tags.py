from django import template
from django.template.loader import get_template

register = template.Library()


@register.simple_tag(takes_context=True)
def context_template(context, template_name):
    gebruiker = context.get("request").user
    context_instance = (
        gebruiker.profiel.context
        if gebruiker and gebruiker.profiel and gebruiker.profiel.context
        else None
    )
    default_template = f"standaard/{template_name}"
    if not context_instance:
        return default_template
    try:
        get_template(f"{context_instance.template}/{template_name}")
    except Exception as e:
        return default_template
    return f"{context_instance.template}/{template_name}"
