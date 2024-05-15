import logging

from apps.services.basis import BasisService
from django.conf import settings

logger = logging.getLogger(__name__)


class TaakRService(BasisService):
    _default_error_message = "Er ging iets mis met het ophalen van data van TaakR"

    def __init__(self, *args, **kwargs: dict):
        self._api_base_url = settings.TAAKR_URL
        super().__init__(*args, **kwargs)

    def get_afdelingen(self, url) -> dict:
        alle_afdelingen = []
        next_page = f"{self._api_base_url}/api/v1/afdeling"
        while next_page:
            response = self.do_request(
                next_page, cache_timeout=60 * 60, raw_response=False
            )
            current_afdelingen = response.get("results", [])
            alle_afdelingen.extend(current_afdelingen)
            next_page = response.get("next")
        return alle_afdelingen

    def get_taaktypes(self, use_cache=True):
        alle_taaktypes = []
        next_page = f"{self._api_base_url}/api/v1/taaktype"
        while next_page:
            response = self.do_request(
                next_page,
                cache_timeout=60 * 60,
                force_cache=not use_cache,
                raw_response=False,
            )
            current_taaktypes = response.get("results", [])
            alle_taaktypes.extend(current_taaktypes)
            next_page = response.get("next")
        return alle_taaktypes

    def get_taaktype(self, taaktype_uuid):
        url = f"{self._api_base_url}/api/v1/taaktype/{taaktype_uuid}"
        taaktype = self.do_request(
            url,
            cache_timeout=60 * 60,
            raw_response=False,
        )
        return taaktype
