import logging

from celery import current_app as celery_app
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.views import View

from apps.main.services.pending_batch import COUNTDOWN, MARGE, MAX_PAUSE_DUUR, PendingBatchService
from apps.main.tasks import verstuur_batch_naar_mor_core

logger = logging.getLogger(__name__)


class TakenVerstuurView(PermissionRequiredMixin, View):
    permission_required = "authorisatie.taak_aanmaken"

    def post(self, request, id, batch_uuid):
        service = PendingBatchService()
        batch = service.ophalen(batch_uuid)

        if batch is None:
            return JsonResponse({"error": "Batch niet gevonden"}, status=404)

        # Revoke the task
        if batch.get("celery_task_id"):
            celery_app.control.revoke(batch["celery_task_id"])

        # Verstuur direct via Celery (countdown=0)
        verstuur_batch_naar_mor_core.apply_async(
            args=[batch_uuid],
            countdown=0,
        )

        return JsonResponse({"status": "ok"})


class TakenAnnuleerView(PermissionRequiredMixin, View):
    permission_required = "authorisatie.taak_aanmaken"

    def post(self, request, id, batch_uuid, taak_uuid):
        service = PendingBatchService()
        result = service.annuleer_taak(batch_uuid, taak_uuid)

        if result is None:
            return JsonResponse({"error": "Batch niet gevonden"}, status=404)

        # Als alle taken geannuleerd zijn, revoke
        if result["alles_geannuleerd"]:
            batch = service.ophalen(batch_uuid)
            if batch and batch.get("celery_task_id"):
                celery_app.control.revoke(batch["celery_task_id"])
            service.verwijderen(batch_uuid)

        return JsonResponse({
            "geannuleerde_uuids": result["geannuleerde_uuids"],
            "alles_geannuleerd": result["alles_geannuleerd"],
        })


class TakenPauseView(PermissionRequiredMixin, View):
    permission_required = "authorisatie.taak_aanmaken"

    def patch(self, request, id, batch_uuid, taak_uuid):
        service = PendingBatchService()
        batch = service.pause_taak(batch_uuid, taak_uuid)

        if batch is None:
            return JsonResponse({"error": "Batch niet gevonden"}, status=404)

        # Revoke huidige, schedule nieuw met max pause duur
        if batch.get("celery_task_id"):
            celery_app.control.revoke(batch["celery_task_id"])

        result = verstuur_batch_naar_mor_core.apply_async(
            args=[batch_uuid],
            countdown=MAX_PAUSE_DUUR + MARGE,
        )
        service.update_celery_task_id(batch_uuid, result.id)

        return JsonResponse({"status": "paused"})


class TakenResumeView(PermissionRequiredMixin, View):
    permission_required = "authorisatie.taak_aanmaken"

    def patch(self, request, id, batch_uuid, taak_uuid):
        service = PendingBatchService()
        batch = service.resume_taak(batch_uuid, taak_uuid)

        if batch is None:
            return JsonResponse({"error": "Batch niet gevonden"}, status=404)

        # Revoke huidige, schedule nieuw met standaard countdown
        if batch.get("celery_task_id"):
            celery_app.control.revoke(batch["celery_task_id"])

        result = verstuur_batch_naar_mor_core.apply_async(
            args=[batch_uuid],
            countdown=COUNTDOWN + MARGE,
        )
        service.update_celery_task_id(batch_uuid, result.id)

        return JsonResponse({"status": "resumed"})
