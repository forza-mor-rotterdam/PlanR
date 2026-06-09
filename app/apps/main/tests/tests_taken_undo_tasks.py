from unittest.mock import MagicMock, patch

from django.test import TestCase

from apps.main.models import PendingBatch
from apps.main.services.pending_batch import PendingBatchService


class VerstuurBatchNaarMorCoreTests(TestCase):
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

    @patch("apps.main.tasks.MORCoreService")
    def test_verstuurt_pending_taken_en_markeert_sent(self, MockMORCoreService):
        from apps.main.tasks import verstuur_batch_naar_mor_core

        mock_service = MagicMock()
        mock_service.taak_aanmaken.return_value = {
            "_links": {"self": {"href": "http://core/taak/1"}},
        }
        MockMORCoreService.return_value = mock_service

        batch = self.service.aanmaken(self.taken)
        verstuur_batch_naar_mor_core(batch["batch_uuid"])

        self.assertEqual(mock_service.taak_aanmaken.call_count, 2)
        opgehaald = self.service.ophalen(batch["batch_uuid"])
        self.assertEqual(opgehaald["status"], PendingBatch.STATUS_SENT)
        self.assertTrue(all(t["status"] == "sent" for t in opgehaald["taken"]))

    @patch("apps.main.tasks.MORCoreService")
    def test_skipt_cancelled_taken(self, MockMORCoreService):
        from apps.main.tasks import verstuur_batch_naar_mor_core

        mock_service = MagicMock()
        mock_service.taak_aanmaken.return_value = {
            "_links": {"self": {"href": "http://core/taak/1"}},
        }
        MockMORCoreService.return_value = mock_service

        batch = self.service.aanmaken(self.taken)
        self.service.annuleer_taak(batch["batch_uuid"], "bbb")
        verstuur_batch_naar_mor_core(batch["batch_uuid"])

        self.assertEqual(mock_service.taak_aanmaken.call_count, 1)
        self.assertEqual(
            mock_service.taak_aanmaken.call_args_list[0][1]["titel"], "Taak A"
        )

    @patch("apps.main.tasks.MORCoreService")
    def test_behandelt_paused_als_pending(self, MockMORCoreService):
        from apps.main.tasks import verstuur_batch_naar_mor_core

        mock_service = MagicMock()
        mock_service.taak_aanmaken.return_value = {
            "_links": {"self": {"href": "http://core/taak/1"}},
        }
        MockMORCoreService.return_value = mock_service

        batch = self.service.aanmaken(self.taken)
        self.service.pause_taak(batch["batch_uuid"], "aaa")
        verstuur_batch_naar_mor_core(batch["batch_uuid"])

        self.assertEqual(mock_service.taak_aanmaken.call_count, 2)

    @patch("apps.main.tasks.logger")
    @patch("apps.main.tasks.MORCoreService")
    def test_ontbrekende_batch_logt_error_geen_silent_success(
        self, MockMORCoreService, mock_logger
    ):
        from apps.main.tasks import verstuur_batch_naar_mor_core

        mock_service = MagicMock()
        MockMORCoreService.return_value = mock_service

        verstuur_batch_naar_mor_core("niet-bestaand-uuid")

        mock_service.taak_aanmaken.assert_not_called()
        mock_logger.error.assert_called_once()

    @patch("apps.main.tasks.MORCoreService")
    def test_al_sent_batch_is_noop(self, MockMORCoreService):
        from apps.main.tasks import verstuur_batch_naar_mor_core

        mock_service = MagicMock()
        mock_service.taak_aanmaken.return_value = {
            "_links": {"self": {"href": "http://core/taak/1"}},
        }
        MockMORCoreService.return_value = mock_service

        batch = self.service.aanmaken(self.taken)
        verstuur_batch_naar_mor_core(batch["batch_uuid"])  # -> SENT
        verstuur_batch_naar_mor_core(batch["batch_uuid"])  # opnieuw

        # Geen dubbele verzending bij her-invocatie.
        self.assertEqual(mock_service.taak_aanmaken.call_count, 2)

    @patch("apps.main.tasks.MORCoreService")
    def test_alle_cancelled_verstuurt_niks(self, MockMORCoreService):
        from apps.main.tasks import verstuur_batch_naar_mor_core

        mock_service = MagicMock()
        MockMORCoreService.return_value = mock_service

        batch = self.service.aanmaken(self.taken)
        self.service.annuleer_taak(batch["batch_uuid"], "aaa")  # cascade -> bbb
        verstuur_batch_naar_mor_core(batch["batch_uuid"])

        mock_service.taak_aanmaken.assert_not_called()

    @patch("apps.main.tasks.MORCoreService")
    def test_resolved_parents_worden_meegegeven(self, MockMORCoreService):
        from apps.main.tasks import verstuur_batch_naar_mor_core

        mock_service = MagicMock()
        mock_service.taak_aanmaken.side_effect = [
            {"_links": {"self": {"href": "http://core/taak/aaa-url"}}},
            {"_links": {"self": {"href": "http://core/taak/bbb-url"}}},
        ]
        MockMORCoreService.return_value = mock_service

        batch = self.service.aanmaken(self.taken)
        verstuur_batch_naar_mor_core(batch["batch_uuid"])

        second_call_kwargs = mock_service.taak_aanmaken.call_args_list[1][1]
        self.assertEqual(
            second_call_kwargs["afhankelijkheid"],
            [{"taakopdracht_url": "http://core/taak/aaa-url"}],
        )

    @patch("apps.main.tasks.MORCoreService")
    def test_geeft_taak_uuids_door_als_idempotency_key(self, MockMORCoreService):
        from apps.main.tasks import verstuur_batch_naar_mor_core

        mock_service = MagicMock()
        mock_service.taak_aanmaken.return_value = {
            "_links": {"self": {"href": "http://core/taak/x"}}
        }
        MockMORCoreService.return_value = mock_service

        batch = self.service.aanmaken(self.taken)
        verstuur_batch_naar_mor_core(batch["batch_uuid"])

        ontvangen_uuids = [
            kall.kwargs.get("uuid")
            for kall in mock_service.taak_aanmaken.call_args_list
        ]
        self.assertEqual(ontvangen_uuids, ["aaa", "bbb"])

    @patch("apps.main.tasks.MORCoreService")
    def test_fout_zet_status_error_zonder_retry_en_behoudt_verstuurde(
        self, MockMORCoreService
    ):
        from apps.main.tasks import verstuur_batch_naar_mor_core

        # A slaagt, B faalt. Geen retry: status=error, A blijft behouden.
        mock_service = MagicMock()
        mock_service.taak_aanmaken.side_effect = [
            {"_links": {"self": {"href": "http://core/taak/aaa-url"}}},
            Exception("netwerkprobleem"),
        ]
        MockMORCoreService.return_value = mock_service

        batch = self.service.aanmaken(self.taken)
        # Geen exception meer naar buiten: de task vangt 'm en zet status=error.
        verstuur_batch_naar_mor_core(batch["batch_uuid"])

        obj = PendingBatch.objects.get(batch_uuid=batch["batch_uuid"])
        self.assertEqual(obj.status, PendingBatch.STATUS_ERROR)
        taak_a = next(t for t in obj.taken if t["uuid"] == "aaa")
        taak_b = next(t for t in obj.taken if t["uuid"] == "bbb")
        self.assertEqual(taak_a["status"], "sent")
        self.assertEqual(taak_a["taakopdracht_url"], "http://core/taak/aaa-url")
        self.assertEqual(taak_b["status"], "pending")
