import celery
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

DEFAULT_RETRY_DELAY = 2
MAX_RETRIES = 6

LOCK_EXPIRE = 5


class BaseTaskWithRetry(celery.Task):
    autoretry_for = (Exception,)
    max_retries = MAX_RETRIES
    default_retry_delay = DEFAULT_RETRY_DELAY


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_aanmaken_afbeelding_versies(self, bijlage_id):
    from apps.release_notes.models import Bijlage

    bijlage_instance = Bijlage.objects.get(id=bijlage_id)
    bijlage_instance.aanmaken_afbeelding_versies()
    bijlage_instance.save()

    return f"Bijlage id: {bijlage_instance.id}"


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_activeer_notificatie(self, notificatie_id):
    from apps.main.services import MercureService
    from apps.release_notes.models import ReleaseNote
    from django.template.loader import render_to_string

    notificatie = ReleaseNote.objects.get(id=notificatie_id)

    rendered = render_to_string(
        "public/notificaties/snack_item.html",
        {
            "notificatie": notificatie,
            "target": "snack_lijst",
            "action": "prepend",
        },
    )
    topic = "/notificaties/snack/"
    MercureService().publish(topic, data=rendered)

    return f"Activeren notificatie met id: {notificatie.id}"
