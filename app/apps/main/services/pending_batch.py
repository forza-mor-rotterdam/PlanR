import json
import logging
import uuid as uuid_lib

from django.core.cache import cache

logger = logging.getLogger(__name__)

BATCH_CACHE_PREFIX = "pending_batch"
COUNTDOWN = 10  # seconds before auto-send
MARGE = 10  # seconds extra before Celery fallback fires
MAX_PAUSE_DUUR = 60  # seconds max pause duration
# TTL must outlive the longest possible delay + safety margin
BATCH_TTL = MAX_PAUSE_DUUR + MARGE + 60  # seconds


class PendingBatchService:
    def _cache_key(self, batch_uuid):
        return f"{BATCH_CACHE_PREFIX}:{batch_uuid}"

    def aanmaken(self, taken, celery_task_id=None):
        batch_uuid = str(uuid_lib.uuid4())
        batch = {
            "batch_uuid": batch_uuid,
            "taken": [
                {
                    "uuid": taak["uuid"],
                    "taak_data": taak["taak_data"],
                    "parents": taak["parents"],
                    "status": "pending",
                }
                for taak in taken
            ],
            "celery_task_id": celery_task_id,
        }
        cache.set(self._cache_key(batch_uuid), json.dumps(batch), BATCH_TTL)
        return batch

    def ophalen(self, batch_uuid):
        data = cache.get(self._cache_key(batch_uuid))
        if data is None:
            return None
        batch = json.loads(data)
        batch["alles_geannuleerd"] = all(
            t["status"] == "cancelled" for t in batch["taken"]
        )
        return batch

    def _opslaan(self, batch):
        cache.set(
            self._cache_key(batch["batch_uuid"]),
            json.dumps(batch),
            BATCH_TTL,
        )

    def annuleer_taak(self, batch_uuid, taak_uuid):
        batch = self.ophalen(batch_uuid)
        if batch is None:
            return None

        # Collect the target + all children (direct and indirect)
        te_annuleren = {taak_uuid}
        changed = True
        while changed:
            changed = False
            for taak in batch["taken"]:
                if taak["uuid"] not in te_annuleren:
                    if any(p in te_annuleren for p in taak["parents"]):
                        te_annuleren.add(taak["uuid"])
                        changed = True

        for taak in batch["taken"]:
            if taak["uuid"] in te_annuleren:
                taak["status"] = "cancelled"

        batch.pop("alles_geannuleerd", None)
        self._opslaan(batch)

        return {
            "geannuleerde_uuids": list(te_annuleren),
            "alles_geannuleerd": all(
                t["status"] == "cancelled" for t in batch["taken"]
            ),
        }

    def pause_taak(self, batch_uuid, taak_uuid):
        batch = self.ophalen(batch_uuid)
        if batch is None:
            return None

        for taak in batch["taken"]:
            if taak["uuid"] == taak_uuid:
                taak["status"] = "paused"
                break

        batch.pop("alles_geannuleerd", None)
        self._opslaan(batch)
        return batch

    def resume_taak(self, batch_uuid, taak_uuid):
        batch = self.ophalen(batch_uuid)
        if batch is None:
            return None

        for taak in batch["taken"]:
            if taak["uuid"] == taak_uuid:
                taak["status"] = "pending"
                break

        batch.pop("alles_geannuleerd", None)
        self._opslaan(batch)
        return batch

    def update_celery_task_id(self, batch_uuid, celery_task_id):
        batch = self.ophalen(batch_uuid)
        if batch is None:
            return None

        batch["celery_task_id"] = celery_task_id
        batch.pop("alles_geannuleerd", None)
        self._opslaan(batch)
        return batch

    def verwijderen(self, batch_uuid):
        cache.delete(self._cache_key(batch_uuid))
