from django.test import TestCase

from apps.main.models import PendingBatch
from apps.main.services.pending_batch import PendingBatchService


class PendingBatchServiceTests(TestCase):
    def setUp(self):
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

    def test_aanmaken_slaat_batch_op_in_db(self):
        batch = self.service.aanmaken(self.taken)
        self.assertIn("batch_uuid", batch)
        self.assertTrue(
            PendingBatch.objects.filter(batch_uuid=batch["batch_uuid"]).exists()
        )
        opgehaald = self.service.ophalen(batch["batch_uuid"])
        self.assertEqual(len(opgehaald["taken"]), 2)
        self.assertTrue(all(t["status"] == "pending" for t in opgehaald["taken"]))
        self.assertEqual(opgehaald["status"], PendingBatch.STATUS_STAGED)

    def test_aanmaken_leidt_melding_uuid_af(self):
        batch = self.service.aanmaken(self.taken)
        obj = PendingBatch.objects.get(batch_uuid=batch["batch_uuid"])
        self.assertEqual(obj.melding_uuid, "m1")

    def test_batch_overleeft_lege_cache(self):
        from django.core.cache import cache

        batch = self.service.aanmaken(self.taken)
        cache.clear()  # Redis weg: batch leeft door in Postgres
        opgehaald = self.service.ophalen(batch["batch_uuid"])
        self.assertIsNotNone(opgehaald)
        self.assertEqual(len(opgehaald["taken"]), 2)

    def test_ophalen_niet_bestaand_geeft_none(self):
        self.assertIsNone(self.service.ophalen("niet-bestaand"))

    def test_annuleer_taak_zet_status_cancelled(self):
        batch = self.service.aanmaken(self.taken)
        result = self.service.annuleer_taak(batch["batch_uuid"], "aaa")
        self.assertIn("aaa", result["geannuleerde_uuids"])
        self.assertIn("bbb", result["geannuleerde_uuids"])  # child cascade

    def test_annuleer_taak_zonder_children(self):
        batch = self.service.aanmaken(self.taken)
        result = self.service.annuleer_taak(batch["batch_uuid"], "bbb")
        self.assertIn("bbb", result["geannuleerde_uuids"])
        self.assertNotIn("aaa", result["geannuleerde_uuids"])

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

    def test_verwijder_batch_soft_cancelt(self):
        batch = self.service.aanmaken(self.taken)
        self.service.verwijderen(batch["batch_uuid"])
        obj = PendingBatch.objects.get(batch_uuid=batch["batch_uuid"])
        self.assertEqual(obj.status, PendingBatch.STATUS_CANCELLED)
        # Rij blijft bestaan voor audit; ophalen geeft 'm nog terug.
        self.assertIsNotNone(self.service.ophalen(batch["batch_uuid"]))

    def test_update_celery_task_id(self):
        batch = self.service.aanmaken(self.taken)
        self.service.update_celery_task_id(batch["batch_uuid"], "new-celery-id")
        opgehaald = self.service.ophalen(batch["batch_uuid"])
        self.assertEqual(opgehaald["celery_task_id"], "new-celery-id")
