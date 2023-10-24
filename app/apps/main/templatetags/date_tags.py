from django import template
from utils.datetime import stringdatetime_naar_datetime

register = template.Library()


@register.filter
def to_datetime(value):
    if not value:
        return
    return stringdatetime_naar_datetime(value)
