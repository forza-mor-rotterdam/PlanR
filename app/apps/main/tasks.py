import re

import celery
from apps.main.services import MORCoreService, MercureService
from apps.main.services.pending_batch import PendingBatchService
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


@shared_task(bind=True)
def verstuur_batch_naar_mor_core(self, batch_uuid):
    from apps.main.models import PendingBatch

    obj = PendingBatch.objects.filter(batch_uuid=str(batch_uuid)).first()

    if obj is None:
        # Met een duurzame store betekent "niet gevonden" een echte anomalie
        # (bv. verloren bericht) -- geen stille success meer.
        logger.error(
            f"Batch {batch_uuid} niet gevonden in database; mogelijk verloren."
        )
        return f"Batch {batch_uuid} niet gevonden"

    if obj.status in (PendingBatch.STATUS_SENT, PendingBatch.STATUS_CANCELLED):
        logger.info(f"Batch {batch_uuid} status={obj.status}; niets te doen.")
        return f"Batch {batch_uuid} status={obj.status}"

    obj.status = PendingBatch.STATUS_SENDING
    obj.save()

    mor_core_service = MORCoreService()
    cancelled_uuids = {
        t["uuid"] for t in obj.taken if t["status"] == "cancelled"
    }
    uuid_to_url = {}

    try:
        for taak in obj.taken:
            if taak["status"] == "cancelled":
                continue
            if taak["status"] == "sent":
                # Al verstuurd (defensief bij her-invocatie): url herstellen
                # zodat kinderen hun parent-url kunnen resolven.
                if taak.get("taakopdracht_url"):
                    uuid_to_url[taak["uuid"]] = taak["taakopdracht_url"]
                continue

            taak_data = taak["taak_data"].copy()
            resolved_parents = [
                uuid_to_url.get(p, p)
                for p in taak["parents"]
                if p not in cancelled_uuids
            ]
            taak_data["afhankelijkheid"] = [
                {"taakopdracht_url": url} for url in resolved_parents
            ]

            response = mor_core_service.taak_aanmaken(
                uuid=taak["uuid"], **taak_data
            )
            taakopdracht_url = response.get("_links", {}).get("self")
            taakopdracht_url = (
                taakopdracht_url.get("href")
                if isinstance(taakopdracht_url, dict)
                else taakopdracht_url
            )
            if taakopdracht_url:
                uuid_to_url[taak["uuid"]] = taakopdracht_url
                taak["taakopdracht_url"] = taakopdracht_url
            taak["status"] = "sent"
            obj.save()
    except Exception:
        # Geen retry: markeer error, bewaar reeds verstuurde taken, log.
        obj.status = PendingBatch.STATUS_ERROR
        obj.save()
        logger.exception(
            f"Batch {batch_uuid} versturen mislukt; status=error gezet."
        )
        return f"Batch {batch_uuid} error"

    obj.status = PendingBatch.STATUS_SENT
    obj.save()
    return f"Batch {batch_uuid} verstuurd: {len(uuid_to_url)} taken"
