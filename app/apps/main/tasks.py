import re

import celery
from apps.main.services import MercureService
from apps.main.utils import publiceer_topic_met_subscriptions
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
def publiseer_melding_gebruikers_activiteiten(self):
    mercure_service = None
    try:
        mercure_service = MercureService()
    except MercureService.ConfigException:
        return "MercureService.ConfigException error"

    alle_subscriptions = mercure_service.get_subscriptions()
    subscriptions = alle_subscriptions.get("subscriptions", [])

    pat = r"/melding/[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}/"
    melding_subscriptions = [
        subscription
        for subscription in subscriptions
        if re.compile(pat).match(subscription.get("topic"))
    ]
    topics = list(
        set(
            [
                subscription.get("topic")
                for subscription in melding_subscriptions
                if subscription.get("topic")
            ]
        )
    )
    for topic in topics:
        publiceer_topic_met_subscriptions(topic, melding_subscriptions)

    return f"Topics gepubliceerd: {topics}"
