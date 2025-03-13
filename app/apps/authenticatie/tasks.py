from apps.authenticatie.models import Gebruiker
from apps.main.services import MORCoreService
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(bind=True)
def publiceer_alle_gebruikers(self):
    gebruikers = Gebruiker.objects.all()
    for gebruiker in gebruikers:
        MORCoreService().set_gebruiker(
            gebruiker=gebruiker.serialized_instance(),
        )
    return f"Gebruikers gepubliceerd: aantal={gebruikers.count()}"
