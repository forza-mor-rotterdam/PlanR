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


@shared_task(bind=True, base=BaseTaskWithRetry)
def verstuur_batch_naar_mor_core(self, batch_uuid):
    service = PendingBatchService()
    batch = service.ophalen(batch_uuid)

    if batch is None:
        logger.info(f"Batch {batch_uuid} niet gevonden, al verwerkt.")
        return f"Batch {batch_uuid} niet gevonden"

    mor_core_service = MORCoreService()
    uuid_to_url = {}

    for taak in batch["taken"]:
        if taak["status"] == "cancelled":
            continue

        # Edge case: user hovert over undo knop en de browser crasht.
        # De timer wordt niet herstart. Om deze reden hebben wij een max pauze tijd van 60 sec.
        # Zie MAX_PAUSE_DUUR in tasks.py

        taak_data = taak["taak_data"].copy()
        # Resolve parent UUIDs to MOR Core URLs
        resolved_parents = [
            uuid_to_url.get(p, p) for p in taak["parents"]
            if p not in [
                t["uuid"]
                for t in batch["taken"]
                if t["status"] == "cancelled"
            ]
        ]
        taak_data["afhankelijkheid"] = [
            {"taakopdracht_url": url} for url in resolved_parents
        ]

        response = mor_core_service.taak_aanmaken(**taak_data)
        taakopdracht_url = response.get("_links", {}).get("self")
        taakopdracht_url = (
            taakopdracht_url.get("href")
            if isinstance(taakopdracht_url, dict)
            else taakopdracht_url
        )
        if taakopdracht_url:
            uuid_to_url[taak["uuid"]] = taakopdracht_url

    service.verwijderen(batch_uuid)
    return f"Batch {batch_uuid} verstuurd: {len(uuid_to_url)} taken"
