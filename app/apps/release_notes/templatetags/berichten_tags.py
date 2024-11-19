from apps.release_notes.models import ReleaseNote
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def is_unwatched_by_user(context, bericht):
    if isinstance(bericht, ReleaseNote):
        return bericht.is_unwatched_by_user(context.request.user)
    return False
