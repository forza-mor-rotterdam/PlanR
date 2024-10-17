import calendar
from datetime import datetime, timedelta

import celery
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

DEFAULT_RETRY_DELAY = 2
MAX_RETRIES = 1


class BaseTaskWithRetry(celery.Task):
    autoretry_for = (Exception,)
    max_retries = MAX_RETRIES
    default_retry_delay = DEFAULT_RETRY_DELAY


@shared_task(bind=True, base=BaseTaskWithRetry)
def dagen_aanmaken(self):
    from apps.dashboard.models import (
        DoorlooptijdenAfgehandeldeMeldingen,
        NieuweMeldingAantallen,
        NieuweSignaalAantallen,
        NieuweTaakopdrachten,
        StatusVeranderingDuurMeldingen,
        TaakopdrachtDoorlooptijden,
        TaaktypeAantallenPerMelding,
    )

    tijdsvak_classes = (
        DoorlooptijdenAfgehandeldeMeldingen,
        StatusVeranderingDuurMeldingen,
        NieuweMeldingAantallen,
        NieuweSignaalAantallen,
        NieuweTaakopdrachten,
        TaaktypeAantallenPerMelding,
        TaakopdrachtDoorlooptijden,
    )
    start_datumtijd = datetime(2023, 1, 1)
    tijdsvakken = []
    while start_datumtijd < (datetime.now() - timedelta(days=1)):
        for cls in tijdsvak_classes:
            try:
                tijdsvak = cls(start_datumtijd=start_datumtijd)
                tijdsvak.save()
                tijdsvakken.append(tijdsvak)
            except Exception:
                ...

        start_datumtijd = start_datumtijd + timedelta(days=1)

    return {
        "tijdsvakken_aangemaakt": len(tijdsvakken),
    }


@shared_task(bind=True, base=BaseTaskWithRetry)
def maanden_aanmaken(self):
    from apps.dashboard.models import (
        DoorlooptijdenAfgehandeldeMeldingen,
        NieuweMeldingAantallen,
        NieuweSignaalAantallen,
        NieuweTaakopdrachten,
        StatusVeranderingDuurMeldingen,
        TaakopdrachtDoorlooptijden,
        TaaktypeAantallenPerMelding,
        Tijdsvak,
    )

    start_datumtijd = datetime(2023, 1, 1)
    now = datetime.now()
    tijdsvak_classes = (
        DoorlooptijdenAfgehandeldeMeldingen,
        StatusVeranderingDuurMeldingen,
        NieuweMeldingAantallen,
        NieuweSignaalAantallen,
        NieuweTaakopdrachten,
        TaaktypeAantallenPerMelding,
        TaakopdrachtDoorlooptijden,
    )
    tijdsvakken = []
    while start_datumtijd < (datetime(now.year, now.month, 1) - timedelta(days=1)):
        for cls in tijdsvak_classes:
            try:
                tijdsvak = cls(
                    start_datumtijd=start_datumtijd,
                    periode=Tijdsvak.PeriodeOpties.MAAND,
                )
                tijdsvak.save()
                tijdsvakken.append(tijdsvak)
            except Exception:
                ...

        start_datumtijd = start_datumtijd + timedelta(
            days=calendar.monthrange(start_datumtijd.year, start_datumtijd.month)[1]
        )

    return {
        "tijdsvakken_aangemaakt": len(tijdsvakken),
    }


@shared_task(bind=True, base=BaseTaskWithRetry)
def tijdsvakdata_vernieuwen(self):
    from apps.dashboard.models import Tijdsvak

    tijdsvakken = Tijdsvak.objects.filter(valide_data=False)
    for tijdsvak in tijdsvakken:
        tijdsvakitem_data_vernieuwen.delay(tijdsvak.id)

    return {
        "aantal_tijdsvakken": tijdsvakken.count(),
    }


@shared_task(bind=True, base=BaseTaskWithRetry)
def tijdsvakitem_data_vernieuwen(self, tijdsvak_id):
    from apps.dashboard.models import Tijdsvak
    from apps.services.meldingen import MeldingenService

    tijdsvak = Tijdsvak.objects.get(id=tijdsvak_id)
    try:
        resultaat = MeldingenService().tijdsvak_data_halen(
            url=tijdsvak.databron.url,
            params={
                tijdsvak.databron.start_datumtijd_param: tijdsvak.start_datumtijd.isoformat(),
                tijdsvak.databron.eind_datumtijd_param: tijdsvak.eind_datumtijd.isoformat(),
            },
        )
        logger.info(resultaat)
        tijdsvak.valide_data = True
        tijdsvak.resultaat = resultaat
    except Exception as e:
        ee = None
        try:
            tijdsvak.valide_data = False
            tijdsvak.save()
        except Exception:
            ...
        logger.error(f"Er ging iets mis: {e}, {ee}")
        raise Exception(f"Er ging iets mis: {e}, {ee}")

    tijdsvak.save()

    return {
        "tijdsvak_id": tijdsvak.id,
    }
