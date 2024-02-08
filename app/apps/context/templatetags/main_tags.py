from django import template

register = template.Library()


@register.simple_tag
def slice_iterable(input, start_int=None, end_int=None):
    try:
        iter(input)
    except TypeError:
        return input
    if start_int is not None and not isinstance(start_int, int):
        return input
    if end_int is not None and not isinstance(end_int, int):
        return input
    if not start_int and not end_int:
        return input
    if start_int is None:
        return input[:end_int]
    if end_int is None:
        return input[start_int:]
    return input[start_int:end_int]
