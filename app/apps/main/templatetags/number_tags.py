from django import template

register = template.Library()


@register.filter
def to_abs(number):
    return abs(number)
