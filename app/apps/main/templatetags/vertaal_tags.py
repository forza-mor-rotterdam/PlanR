from apps.main.constanten import VERTALINGEN
from django import template

register = template.Library()


@register.filter
def vertaal(value):
    return VERTALINGEN.get(value, value)
