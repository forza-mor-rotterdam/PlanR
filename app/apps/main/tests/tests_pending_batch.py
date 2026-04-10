import json
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase, override_settings

from apps.main.services.pending_batch import PendingBatchService


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
)
class PendingBatchServiceTests(TestCase):
    def setUp(self):
        cache.clear()
        self.service = PendingBatchService()
        self.taken = [
            {
                "uuid": "aaa",
                "taak_data": {
                    "melding_uuid": "m1",
                    "titel": "Taak A",
                    "taakapplicatie_taaktype_url": "http://taakr/1",
                    "bericht": "",
                    "gebruiker": "user@test.nl",
                    "afhankelijkheid": [],
                },
                "parents": [],
            },
            {
                "uuid": "bbb",
                "taak_data": {
                    "melding_uuid": "m1",
                    "titel": "Taak B",
                    "taakapplicatie_taaktype_url": "http://taakr/2",
                    "bericht": "",
                    "gebruiker": "user@test.nl",
                    "afhankelijkheid": [],
                },
                "parents": ["aaa"],
            },
        ]

    def test_aanmaken_slaat_batch_op_in_cache(self):
        batch = self.service.aanmaken(self.taken)
        self.assertIn("batch_uuid", batch)
        opgehaald = self.service.ophalen(batch["batch_uuid"])
        self.assertEqual(len(opgehaald["taken"]), 2)
        self.assertTrue(
            all(t["status"] == "pending" for t in opgehaald["taken"])
        )

    def test_ophalen_niet_bestaand_geeft_none(self):
        self.assertIsNone(self.service.ophalen("niet-bestaand"))

    def test_annuleer_taak_zet_status_cancelled(self):
        batch = self.service.aanmaken(self.taken)
        result = self.service.annuleer_taak(batch["batch_uuid"], "aaa")
        geannuleerde_uuids = result["geannuleerde_uuids"]
        self.assertIn("aaa", geannuleerde_uuids)
        self.assertIn("bbb", geannuleerde_uuids)  # child cascade

    def test_annuleer_taak_zonder_children(self):
        batch = self.service.aanmaken(self.taken)
        result = self.service.annuleer_taak(batch["batch_uuid"], "bbb")
        geannuleerde_uuids = result["geannuleerde_uuids"]
        self.assertIn("bbb", geannuleerde_uuids)
        self.assertNotIn("aaa", geannuleerde_uuids)

    def test_annuleer_alle_taken_geeft_alle_cancelled(self):
        batch = self.service.aanmaken(self.taken)
        self.service.annuleer_taak(batch["batch_uuid"], "aaa")
        opgehaald = self.service.ophalen(batch["batch_uuid"])
        self.assertTrue(
            all(t["status"] == "cancelled" for t in opgehaald["taken"])
        )
        self.assertTrue(opgehaald["alles_geannuleerd"])

    def test_pause_taak_zet_status_paused(self):
        batch = self.service.aanmaken(self.taken)
        self.service.pause_taak(batch["batch_uuid"], "aaa")
        opgehaald = self.service.ophalen(batch["batch_uuid"])
        taak_a = next(t for t in opgehaald["taken"] if t["uuid"] == "aaa")
        self.assertEqual(taak_a["status"], "paused")

    def test_resume_taak_zet_status_pending(self):
        batch = self.service.aanmaken(self.taken)
        self.service.pause_taak(batch["batch_uuid"], "aaa")
        self.service.resume_taak(batch["batch_uuid"], "aaa")
        opgehaald = self.service.ophalen(batch["batch_uuid"])
        taak_a = next(t for t in opgehaald["taken"] if t["uuid"] == "aaa")
        self.assertEqual(taak_a["status"], "pending")

    def test_verwijder_batch(self):
        batch = self.service.aanmaken(self.taken)
        self.service.verwijderen(batch["batch_uuid"])
        self.assertIsNone(self.service.ophalen(batch["batch_uuid"]))

    def test_update_celery_task_id(self):
        batch = self.service.aanmaken(self.taken)
        self.service.update_celery_task_id(batch["batch_uuid"], "new-celery-id")
        opgehaald = self.service.ophalen(batch["batch_uuid"])
        self.assertEqual(opgehaald["celery_task_id"], "new-celery-id")

    def test_get_actieve_taken(self):
        batch = self.service.aanmaken(self.taken)
        self.service.annuleer_taak(batch["batch_uuid"], "bbb")
        opgehaald = self.service.ophalen(batch["batch_uuid"])
        actieve = [t for t in opgehaald["taken"] if t["status"] != "cancelled"]
        self.assertEqual(len(actieve), 1)
        self.assertEqual(actieve[0]["uuid"], "aaa")
