import logging

from apps.services.basis import BasisService

logger = logging.getLogger(__name__)


def render_onderwerp(onderwerp_url, standaar_naam=None):
    onderwerp = OnderwerpenService().get_onderwerp(onderwerp_url)
    standaard_naam = onderwerp.get(
        "name", "Niet gevonden!" if not standaar_naam else standaar_naam
    )
    return standaard_naam


class OnderwerpenService(BasisService):
    def get_onderwerp(self, url) -> dict:
        return self.do_request(url, cache_timeout=120, raw_response=False)
