from apps.main.models import SPECIFICATIE_CACHE_TIMEOUT
from apps.main.services import MORCoreService
from django import template

register = template.Library()


@register.filter
def specificatie_naam(specificatie_url):
    padden = specificatie_url.split("?")[0].strip("/").split("/")
    if not padden:
        return "-"
    specificatie_uuid = padden[-1]
    specificatie = MORCoreService().specificatie_detail(
        specificatie_uuid=specificatie_uuid,
        force_cache=True,
        cache_timeout=SPECIFICATIE_CACHE_TIMEOUT,
    )
    return specificatie.get("naam", "-")
