import logging

from apps.instellingen.models import Instelling
from django.contrib import messages
from mor_api_services import LocatieService as BasisLocatieService
from mor_api_services import MercureService as BasisMercureService
from mor_api_services import MORCoreService as BasisMORCoreService
from mor_api_services import OnderwerpenService as BasisOnderwerpenService
from mor_api_services import TaakRService as BasisTaakRService

logger = logging.getLogger(__name__)


def standaard_fout_afhandeling(service, response=None, fout=""):
    log = (
        f"API antwoord fout: {service.naar_json(response)}, status code: {response.status_code}"
        if not fout
        else f"Generiek fout: {fout}"
    )
    logger.error(log)

    message = (
        f'Er ging iets mis!: {service.naar_json(response).get("detail", "Geen detail gevonden")}, {service.__class__.__name__}[{response.status_code}]'
        if not fout
        else f"Er ging iets mis!: {service.__class__.__name__}"
    )
    if service._request:
        messages.error(service._request, message)

    return {
        "error": log,
    }


class MORCoreService(BasisMORCoreService):
    def __init__(self, *args, **kwargs):
        instellingen = Instelling.actieve_instelling()
        kwargs.update(
            {
                "basis_url": instellingen.mor_core_basis_url,
                "client_name": "PlanR",
                "gebruikersnaam": instellingen.mor_core_gebruiker_email,
                "wachtwoord": instellingen.mor_core_gebruiker_wachtwoord,
                "token_timeout": instellingen.mor_core_token_timeout,
            }
        )
        super().__init__(*args, **kwargs)

    def met_fout(self, response=None, fout=""):
        return standaard_fout_afhandeling(self, response, fout)


class OnderwerpenService(BasisOnderwerpenService):
    def __init__(self, *args, **kwargs):
        instellingen = Instelling.actieve_instelling()
        kwargs.update(
            {
                "basis_url": instellingen.onderwerpen_basis_url,
            }
        )
        super().__init__(*args, **kwargs)

    def met_fout(self, response=None, fout=""):
        return standaard_fout_afhandeling(self, response, fout)


class TaakRService(BasisTaakRService):
    def __init__(self, *args, **kwargs):
        default_cache_timeout = 60 * 60 * 24
        instellingen = Instelling.actieve_instelling()
        kwargs.update(
            {
                "basis_url": instellingen.taakr_basis_url,
                "cache_timeout": kwargs.get("cache_timeout", default_cache_timeout),
            }
        )
        super().__init__(*args, **kwargs)

    def met_fout(self, response=None, fout=""):
        return standaard_fout_afhandeling(self, response, fout)


class LocatieService(BasisLocatieService):
    def __init__(self, *args, **kwargs):
        instellingen = Instelling.actieve_instelling()
        default_cache_timeout = 60 * 60
        kwargs.update(
            {
                "basis_url": instellingen.locaties_basis_url,
                "cache_timeout": kwargs.get("cache_timeout", default_cache_timeout),
            }
        )
        super().__init__(*args, **kwargs)

    def met_fout(self, response=None, fout=""):
        return standaard_fout_afhandeling(self, response, fout)


class MercureService(BasisMercureService):
    def __init__(self):
        super().__init__()


def render_onderwerp(onderwerp_url, standaard_naam=None, force_cache=False):
    onderwerp = OnderwerpenService().get_onderwerp(
        onderwerp_url, force_cache=force_cache
    )

    standaard_naam = onderwerp.get(
        "name", "Niet gevonden!" if not standaard_naam else standaard_naam
    )
    return standaard_naam


def render_onderwerp_groepen(context, force_cache=False):
    try:
        groep_uuids = {}
        for key, value in context.items():
            onderwerp_url = value[0]
            onderwerp_data = OnderwerpenService().get_onderwerp(
                onderwerp_url,
                force_cache=force_cache,
            )
            onderwerp_group_uuid = onderwerp_data.get("group_uuid")
            groep_naam = (
                OnderwerpenService()
                .get_groep(
                    onderwerp_group_uuid,
                    force_cache=force_cache,
                )
                .get("name", "")
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
