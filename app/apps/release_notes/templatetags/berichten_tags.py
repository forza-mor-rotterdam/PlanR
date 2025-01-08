from apps.release_notes.models import ReleaseNote
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def is_unwatched_by_user(context, bericht):
    if isinstance(bericht, ReleaseNote):
        return bericht.is_unwatched_by_user(context.request.user)
    return False


@register.simple_tag(takes_context=True)
def toast_context(context):
    message = context.get("message")
    titel = context.get("titel", "")
    niveau = context.get("niveau", "warning")
    id = context.get("id", "")
    return {
        "niveau": niveau if not message else message.tags,
        "titel": titel if not message else message.message,
        "id": id,
    }
