from django import template

register = template.Library()


@register.simple_tag
def slice_iterable(input, start_int, end_int):
    try:
        iter(input)
    except TypeError:
        return input
    if not isinstance(start_int, int) or not isinstance(end_int, int):
        return input

    return input[start_int:end_int]
