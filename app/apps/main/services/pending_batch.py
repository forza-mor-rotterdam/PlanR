import logging
import uuid as uuid_lib
from datetime import timedelta

from django.utils import timezone

from apps.main.models import PendingBatch

logger = logging.getLogger(__name__)

COUNTDOWN = 10  # seconds before auto-send
MARGE = 15  # seconds extra before Celery fallback fires
MAX_PAUSE_DUUR = 90  # seconds max pause duration


class PendingBatchService:
    def _get(self, batch_uuid):
        return PendingBatch.objects.filter(batch_uuid=str(batch_uuid)).first()

    def _to_dict(self, obj):
        return {
            "batch_uuid": obj.batch_uuid,
            "taken": obj.taken,
            "celery_task_id": obj.celery_task_id,
            "status": obj.status,
            "alles_geannuleerd": all(
                t["status"] == "cancelled" for t in obj.taken
            ),
        }

    def aanmaken(self, taken, celery_task_id=None):
        batch_uuid = str(uuid_lib.uuid4())
        taken_data = [
            {
                "uuid": taak["uuid"],
                "taak_data": taak["taak_data"],
                "parents": taak["parents"],
                "taakopdracht_url": None,
                "status": "pending",
            }
            for taak in taken
        ]
        melding_uuid = (
            taken[0]["taak_data"].get("melding_uuid", "") if taken else ""
        )
        obj = PendingBatch.objects.create(
            batch_uuid=batch_uuid,
            melding_uuid=melding_uuid,
            celery_task_id=celery_task_id,
            send_after=timezone.now() + timedelta(seconds=COUNTDOWN + MARGE),
            status=PendingBatch.STATUS_STAGED,
            taken=taken_data,
        )
        return self._to_dict(obj)

    def ophalen(self, batch_uuid):
        obj = self._get(batch_uuid)
        if obj is None:
            return None
        return self._to_dict(obj)

    def annuleer_taak(self, batch_uuid, taak_uuid):
        obj = self._get(batch_uuid)
        if obj is None:
            return None

        # Verzamel de taak + alle (in)directe kinderen.
        te_annuleren = {taak_uuid}
        changed = True
        while changed:
            changed = False
            for taak in obj.taken:
                if taak["uuid"] not in te_annuleren:
                    if any(p in te_annuleren for p in taak["parents"]):
                        te_annuleren.add(taak["uuid"])
                        changed = True

        for taak in obj.taken:
            if taak["uuid"] in te_annuleren:
                taak["status"] = "cancelled"
        obj.save()

        return {
            "geannuleerde_uuids": list(te_annuleren),
            "alles_geannuleerd": all(
                t["status"] == "cancelled" for t in obj.taken
            ),
        }

    def pause_taak(self, batch_uuid, taak_uuid):
        obj = self._get(batch_uuid)
        if obj is None:
            return None
        for taak in obj.taken:
            if taak["uuid"] == taak_uuid:
                taak["status"] = "paused"
                break
        obj.save()
        return self._to_dict(obj)

    def resume_taak(self, batch_uuid, taak_uuid):
        obj = self._get(batch_uuid)
        if obj is None:
            return None
        for taak in obj.taken:
            if taak["uuid"] == taak_uuid:
                taak["status"] = "pending"
                break
        obj.save()
        return self._to_dict(obj)

    def update_celery_task_id(self, batch_uuid, celery_task_id):
        obj = self._get(batch_uuid)
        if obj is None:
            return None
        obj.celery_task_id = celery_task_id
        obj.save()
        return self._to_dict(obj)

    def verwijderen(self, batch_uuid):
        # Soft-cancel: bewaar de rij als audit-trail.
        obj = self._get(batch_uuid)
        if obj is None:
            return
        obj.status = PendingBatch.STATUS_CANCELLED
        obj.save()
