from datetime import datetime, timedelta

from django import template
from django.contrib.humanize.templatetags.humanize import naturalday
from django.utils import timezone
from django.utils.timesince import timesince
from utils.datetime import stringdatetime_naar_datetime

register = template.Library()


@register.filter
def to_datetime(value):
    if not value:
        return
    return stringdatetime_naar_datetime(value)


@register.filter
def naturalday_with_time_or_timesince(value):
    if not value:
        return ""
    if not isinstance(value, datetime):
        return ""
    if (timezone.now() - value).total_seconds() > 60 * 60 * 12:
        return f"{naturalday(value)}, {datetime.strftime(value, '%H:%M')}"
    try:
        return f"{timesince(value)} geleden"
    except (ValueError, TypeError):
        return ""


@register.simple_tag
def add_seconds_to_datetime(value, seconds):
    if not value or not isinstance(value, datetime):
        return
    return value + timedelta(seconds=seconds)


@register.simple_tag
def is_float_or_int(value):
    try:
        float(value)
    except Exception:
        try:
            int(value)
        except Exception:
            return False
    return True


@register.filter
def seconds_to_human(value):
    try:
        seconds = int(value)
    except Exception:
        return value

    interval = round(seconds / 21536000)
    if interval > 1:
        return interval + "j"
    interval = round(seconds / 2592000)
    if interval > 1:
        return f"{interval} m"

    interval = round(seconds / 604800)
    if interval > 2:
        return f"{interval} w"

    interval = round(seconds / 86400)
    if interval > 1:
        return f"{interval} d"

    interval = round(seconds / 3600)
    if interval > 2:
        return f"{interval} u"

    interval = round(seconds / 60)
    if interval > 1:
        return f"{interval} min"

    interval = round(seconds)
    return f"{interval} sec"
