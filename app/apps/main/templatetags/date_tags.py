from django import template
from utils.datetime import stringdatetime_naar_datetime

register = template.Library()


@register.filter
def to_datetime(value):
    if value and isinstance(value, str):
        return stringdatetime_naar_datetime(value)
    return value
