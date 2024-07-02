import logging

from apps.instellingen.models import Instelling
from apps.services.basis import BasisService

logger = logging.getLogger(__name__)


def render_onderwerp(onderwerp_url, standaard_naam=None):
    onderwerp = OnderwerpenService().get_onderwerp(onderwerp_url)

    standaard_naam = onderwerp.get(
        "name", "Niet gevonden!" if not standaard_naam else standaard_naam
    )
    return standaard_naam


def render_onderwerp_groepen(context):
    try:
        groep_uuids = {}
        for key, value in context.items():
            onderwerp_url = value[0]
            onderwerp_data = OnderwerpenService().get_onderwerp(onderwerp_url)
            onderwerp_group_uuid = onderwerp_data.get("group_uuid")
            groep_naam = (
                OnderwerpenService().get_groep(onderwerp_group_uuid).get("name", "")
            )
            if onderwerp_group_uuid not in groep_uuids:
                groep_uuids[onderwerp_group_uuid] = {"naam": groep_naam, "items": []}

            groep_uuids[onderwerp_group_uuid]["items"].append(
                [
                    key,
                    {
                        "label": onderwerp_data.get("name", ""),
                        "item_count": value[1],
                    },
                ]
            )

        onderwerpen_gegroepeerd = [
            [info["naam"], sorted(info["items"], key=lambda b: b[1].get("label"))]
            for groep_uuid, info in groep_uuids.items()
        ]
        return sorted(onderwerpen_gegroepeerd, key=lambda x: x[0])
    except Exception as e:
        logger.error(f"Error onderwerp groep: {e}.")
    return None


class OnderwerpenService(BasisService):
    def __init__(self, *args, **kwargs: dict):
        instelling = Instelling.actieve_instelling()
        if not instelling:
            raise Exception(
                "De Onderwerpen url kon niet worden gevonden, Er zijn nog geen instellingen aangemaakt"
            )
        self._base_url = instelling.onderwerpen_basis_url
        super().__init__(*args, **kwargs)

    # def get_url(self, url):
    #     url_o = urlparse(url)
    #     if not url_o.scheme and not url_o.netloc:
    #         return f"{self._base_url}{url}"
    #     if f"{url_o.scheme}://{url_o.netloc}" == self._base_url:
    #         return url
    #     raise OnderwerpenService.BasisUrlFout(
    #         f"url: {url}, basis_url: {self._base_url}"
    #     )

    def get_onderwerp(self, url) -> dict:
        return self.do_request(url, cache_timeout=60 * 60, raw_response=False)

    def get_onderwerpen(self):
        all_onderwerpen = []
        next_page = f"{self._base_url}/api/v1/category"
        while next_page:
            response = self.do_request(
                next_page, cache_timeout=60 * 60, raw_response=False
            )
            current_onderwerpen = response.get("results", [])
            all_onderwerpen.extend(current_onderwerpen)
            next_page = response.get("_links", {}).get("next")
        return all_onderwerpen

    def get_groep(self, groep_uuid):
        url = f"{self._base_url}/api/v1/group/{groep_uuid}"
        onderwerp_groep = self.do_request(
            url,
            cache_timeout=60 * 60,
            raw_response=False,
        )
        if not onderwerp_groep.get("name"):
            logger.error(
                f"Onderwerp_groep not found: {onderwerp_groep}. Groep url: {url}."
            )
        return onderwerp_groep
