import logging
from urllib.parse import urlparse

from apps.instellingen.models import Instelling
from apps.services.basis import BasisService

logger = logging.getLogger(__name__)


class TaakRService(BasisService):
    _default_error_message = "Er ging iets mis met het ophalen van data van TaakR"

    def __init__(self, *args, **kwargs: dict):
        instelling = Instelling.actieve_instelling()
        if not instelling:
            raise Exception(
                "De TaakR url kon niet worden gevonden, Er zijn nog geen instellingen aangemaakt"
            )
        self._base_url = instelling.taakr_basis_url
        super().__init__(*args, **kwargs)

    def get_url(self, url):
        url_o = urlparse(url)
        if not url_o.scheme and not url_o.netloc:
            return f"{self._base_url}{url}"
        if f"{url_o.scheme}://{url_o.netloc}" == self._base_url:
            return url
        raise TaakRService.BasisUrlFout(f"url: {url}, basis_url: {self._base_url}")

    def get_afdelingen(self, url) -> list:
        alle_afdelingen = []
        next_page = f"{self._base_url}/api/v1/afdeling"
        while next_page:
            response = self.do_request(
                next_page, cache_timeout=60 * 60, raw_response=False
            )
            current_afdelingen = response.get("results", [])
            alle_afdelingen.extend(current_afdelingen)
            next_page = response.get("next")
        return alle_afdelingen

    def get_taaktypes(self, use_cache=True) -> list:
        alle_taaktypes = []
        next_page = f"{self._base_url}/api/v1/taaktype"
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
        url = f"{self._base_url}/api/v1/taaktype/{taaktype_uuid}"
        taaktype = self.do_request(
            url,
            cache_timeout=60 * 60,
            raw_response=False,
        )
        return taaktype

    def get_taaktype_by_url(self, taaktype_url):
        taaktype = self.do_request(
            taaktype_url,
            cache_timeout=0,  # Back to 60*60
            raw_response=False,
        )
        return taaktype

    def get_niet_actieve_taaktypes(self, melding, use_cache=True):
        alle_taaktypes = self.get_taaktypes(use_cache=use_cache)
        gebruikte_taaktypes = [
            *set(
                list(
                    taakopdracht.get("taaktype")
                    for taakopdracht in melding.get("taakopdrachten_voor_melding", [])
                    if not any(
                        taakgebeurtenis.get("resolutie")
                        for taakgebeurtenis in taakopdracht.get(
                            "taakgebeurtenissen_voor_taakopdracht", []
                        )
                    )
                )
            )
        ]

        taaktypes = [
            tt
            for tt in alle_taaktypes
            if tt.get("taakapplicatie_taaktype_url") not in gebruikte_taaktypes
        ]
        return taaktypes

    def categorize_taaktypes(self, melding, taaktypes):
        from apps.context.utils import get_gebruiker_context

        gebruiker_context = get_gebruiker_context(self.request.user)
        taaktypes_categorized = [
            [
                tt.get("_links", {}).get("taakapplicatie_taaktype_url"),
                f"{tt.get('omschrijving')}",
            ]
            for tt in taaktypes
            if tt.get("_links", {}).get("taakapplicatie_taaktype_url")
            in gebruiker_context.taaktypes
            and tt.get("actief", False)
        ]
        gebruikte_taaktypes = [
            *set(
                list(
                    taakopdracht.get("taaktype")
                    for taakopdracht in melding.get("taakopdrachten_voor_melding", [])
                    if not any(
                        taakgebeurtenis.get("resolutie")
                        for taakgebeurtenis in taakopdracht.get(
                            "taakgebeurtenissen_voor_taakopdracht", []
                        )
                    )
                )
            )
        ]
        taaktypes_categorized = [
            tt for tt in taaktypes_categorized if tt[0] not in gebruikte_taaktypes
        ]
        return taaktypes_categorized

    def get_taakapplicatie_taaktype_url(self, taaktype_url):
        if taaktype := self.get_taaktype_by_url(taaktype_url):
            return taaktype.get("_links").get("taakapplicatie_taaktype_url")
