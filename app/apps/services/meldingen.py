import logging
from urllib.parse import urlparse

import requests
from apps.services.basis import BasisService
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

logger = logging.getLogger(__name__)


def get_taaktypes(melding, gebruiker):
    from apps.context.utils import get_gebruiker_context

    gebruiker_context = get_gebruiker_context(gebruiker)

    taakapplicaties = MeldingenService().taakapplicaties()
    taaktypes = [
        [
            tt.get("_links", {}).get("self"),
            f"{tt.get('omschrijving')}",
        ]
        for ta in taakapplicaties.get("results", [])
        for tt in ta.get("taaktypes", [])
        if urlparse(tt.get("_links", {}).get("self")).path
        in [urlparse(tt).path for tt in gebruiker_context.taaktypes]
        and tt.get("actief", False)
    ]
    gebruikte_taaktypes = [
        *set(
            list(
                to.get("taaktype")
                for to in melding.get("taakopdrachten_voor_melding", [])
                if not to.get("resolutie")
            )
        )
    ]
    taaktypes = [tt for tt in taaktypes if tt[0] not in gebruikte_taaktypes]
    return taaktypes


class MeldingenService(BasisService):
    def __init__(self, *args, **kwargs: dict):
        self._api_base_url = settings.MELDINGEN_URL
        super().__init__(*args, **kwargs)

    def get_url(self, url):
        url_o = urlparse(url)
        if not url_o.scheme and not url_o.netloc:
            return f"{self._api_base_url}{url}"
        if f"{url_o.scheme}://{url_o.netloc}" == self._api_base_url:
            return url
        raise MeldingenService.BasisUrlFout(
            f"url: {url}, basis_url: {self._api_base_url}"
        )

    def haal_token(self):
        meldingen_token = cache.get("meldingen_token")
        if not meldingen_token:
            email = settings.MELDINGEN_USERNAME
            try:
                validate_email(email)
            except ValidationError:
                email = f"{settings.MELDINGEN_USERNAME}@forzamor.nl"
            token_response = requests.post(
                settings.MELDINGEN_TOKEN_API,
                json={
                    "username": email,
                    "password": settings.MELDINGEN_PASSWORD,
                },
            )
            if token_response.status_code == 200:
                meldingen_token = token_response.json().get("token")
                cache.set(
                    "meldingen_token", meldingen_token, settings.MELDINGEN_TOKEN_TIMEOUT
                )
            else:
                raise MeldingenService.DataOphalenFout(
                    f"status code: {token_response.status_code}, response text: {token_response.text}"
                )

        return meldingen_token

    def get_headers(self):
        headers = {"Authorization": f"Token {self.haal_token()}"}
        return headers

    def get_melding_lijst(self, query_string=""):
        return self.do_request(
            f"{self._api_path}/melding/?{query_string}",
            raw_response=False,
        )

    def get_melding(self, id, query_string=""):
        return self.do_request(
            f"{self._api_path}/melding/{id}/?{query_string}",
            raw_response=False,
        )

    def melding_gebeurtenis_toevoegen(
        self,
        id,
        bijlagen=[],
        omschrijving_intern=None,
        omschrijving_extern=None,
        gebruiker=None,
    ):
        data = {
            "bijlagen": bijlagen,
            "omschrijving_intern": omschrijving_intern,
            "omschrijving_extern": omschrijving_extern,
            "gebruiker": gebruiker,
        }
        response = self.do_request(
            f"{self._api_path}/melding/{id}/gebeurtenis-toevoegen/",
            method="post",
            data=data,
        )
        if response.status_code != 200:
            raise MeldingenService.AntwoordFout(
                f"status code: {response.status_code}, status code verwacht: 200"
            )
        return response.json()

    def melding_status_aanpassen(
        self,
        id,
        status=None,
        resolutie=None,
        bijlagen=[],
        omschrijving_extern=None,
        omschrijving_intern=None,
        gebruiker=None,
    ):
        data = {
            "bijlagen": bijlagen,
            "omschrijving_extern": omschrijving_extern,
            "omschrijving_intern": omschrijving_intern,
            "gebruiker": gebruiker,
        }
        if status:
            data.update(
                {
                    "status": {
                        "naam": status,
                    },
                    "resolutie": resolutie,
                }
            )
        return self.do_request(
            f"{self._api_path}/melding/{id}/status-aanpassen/"
            if status
            else f"{self._api_path}/melding/{id}/gebeurtenis-toevoegen/",
            method="patch" if status else "post",
            data=data,
            raw_response=False,
        )

    def melding_annuleren(
        self,
        id,
        bijlagen=[],
        omschrijving_intern=None,
        gebruiker=None,
    ):
        data = {
            "bijlagen": bijlagen,
            "omschrijving_intern": omschrijving_intern,
            "gebruiker": gebruiker,
        }
        data.update(
            {
                "status": {
                    "naam": "geannuleerd",
                },
                "resolutie": "opgelost",
            }
        )
        return self.do_request(
            f"{self._api_path}/melding/{id}/status-aanpassen/",
            method="patch",
            data=data,
            raw_response=False,
        )

    def melding_spoed_aanpassen(self, id, urgentie, omschrijving_intern, gebruiker):
        response = self.do_request(
            f"{self._api_path}/melding/{id}/urgentie-aanpassen/",
            method="patch",
            data={
                "urgentie": urgentie,
                "gebruiker": gebruiker,
                "omschrijving_intern": omschrijving_intern,
            },
        )
        if response.status_code == 200:
            return response.json()
        logger.error(response.text)
        raise MeldingenService.DataOphalenFout(
            f"signaal_aanmaken: Verwacht status code 200, kreeg status code '{response.status_code}'"
        )

    def locatie_aanpassen(
        self,
        id,
        omschrijving_intern=None,
        locatie={},
        gebruiker=None,
    ):
        data = {
            "gebruiker": gebruiker,
            "omschrijving_intern": omschrijving_intern,
            "locatie": locatie,
        }
        response = self.do_request(
            f"{self._api_path}/melding/{id}/locatie-aanmaken/",
            method="post",
            data=data,
        )
        if response.status_code // 100 != 2:
            raise MeldingenService.AntwoordFout(
                f"status code: {response.status_code}, fout: {response.text}."
            )
        return response.json()

    def taakapplicaties(self):
        return self.do_request(
            f"{self._api_path}/taakapplicatie/",
            cache_timeout=60,
            raw_response=False,
        )

    def taak_aanmaken(
        self,
        melding_uuid,
        taaktype_url,
        titel,
        bericht=None,
        gebruiker=None,
        additionele_informatie={},
    ):
        data = {
            "taaktype": taaktype_url,
            "titel": titel,
            "bericht": bericht,
            "gebruiker": gebruiker,
            "additionele_informatie": additionele_informatie,
        }
        return self.do_request(
            f"{self._api_path}/melding/{melding_uuid}/taakopdracht/",
            method="post",
            data=data,
            raw_response=False,
        )

    def taak_status_aanpassen(
        self,
        taakopdracht_url,
        status,
        resolutie=None,
        omschrijving_intern=None,
        bijlagen=None,
        gebruiker=None,
    ):
        data = {
            "taakstatus": {
                "naam": status,
            },
            "resolutie": resolutie,
            "omschrijving_intern": omschrijving_intern,
            "bijlagen": bijlagen,
            "gebruiker": gebruiker,
        }
        response = self.do_request(
            f"{taakopdracht_url}status-aanpassen/",
            method="patch",
            data=data,
            raw_response=True,
        )
        if response.status_code == 200:
            return response.json()
        raise MeldingenService.DataOphalenFout(
            f"taak_status_aanpassen: Verwacht status code 200, kreeg status code '{response.status_code}', tekst: {response.text}"
        )

    def signaal_aanmaken(self, data: {}):
        response = self.do_request(
            f"{self._api_path}/signaal/",
            method="post",
            data=data,
        )
        if response.status_code == 201:
            return response.json()
        logger.error(response.text)
        raise MeldingenService.DataOphalenFout(
            f"signaal_aanmaken: Verwacht status code 201, kreeg status code '{response.status_code}'"
        )

    def onderwerp_alias_list(self):
        return self.do_request(
            f"{self._api_path}/onderwerp-alias/",
            cache_timeout=60,
            params={
                "limit": 200,
            },
            raw_response=False,
        )

    def get_gebruiker(self, gebruiker_email):
        return self.do_request(
            f"{self._api_path}/gebruiker/{gebruiker_email}/",
            method="get",
        )

    def set_gebruiker(self, gebruiker):
        return self.do_request(
            f"{self._api_path}/gebruiker/", method="post", data=gebruiker
        )
