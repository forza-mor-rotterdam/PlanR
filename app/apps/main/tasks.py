import celery
from apps.main.utils import publiceer_topic_met_subscriptions
from apps.services.mercure import MercureService
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

    alle_subscriptions = mercure_service.get_subscriptions().get("subscriptions", [])

    topics = list(
        set(
            [
                subscription.get("topic")
                for subscription in alle_subscriptions
                if subscription.get("topic")
            ]
        )
    )
    print(topics)
    for topic in topics:
        publiceer_topic_met_subscriptions(topic, alle_subscriptions)

    return f"Topics gepubliceerd: {topics}"
