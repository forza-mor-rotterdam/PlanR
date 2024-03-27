import json

from django import template

register = template.Library()


@register.filter
def json_encode(value):
    return json.dumps(value)


@register.filter
def json_loads(value):
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return None
