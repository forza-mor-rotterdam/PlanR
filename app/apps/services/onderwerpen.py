import logging

from apps.services.basis import BasisService
from django.conf import settings

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
                OnderwerpenService().get_groep(onderwerp_group_uuid).get("name")
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
        logger.error(f"Error onderwerp groep: {e}")
    return None


class OnderwerpenService(BasisService):
    def get_onderwerp(self, url) -> dict:
        return self.do_request(url, cache_timeout=120, raw_response=False)

    def get_onderwerpen(self):
        all_onderwerpen = []
        next_page = f"{settings.ONDERWERPEN_URL}/api/v1/category"
        while next_page:
            response = self.do_request(next_page, cache_timeout=120, raw_response=False)
            current_onderwerpen = response.get("results", [])
            all_onderwerpen.extend(current_onderwerpen)
            next_page = response.get("_links", {}).get("next")
        return all_onderwerpen

    def get_groep(self, groep_uuid):
        onderwerp_groep = self.do_request(
            f"{settings.ONDERWERPEN_URL}/api/v1/group/{groep_uuid}",
            cache_timeout=120,
            raw_response=False,
        )
        return onderwerp_groep
