import json
from unittest.mock import MagicMock, patch

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
class VerstuurBatchNaarMorCoreTests(TestCase):
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

    @patch("apps.main.tasks.MORCoreService")
    def test_verstuurt_pending_taken_naar_mor_core(self, MockMORCoreService):
        from apps.main.tasks import verstuur_batch_naar_mor_core

        mock_service = MagicMock()
        mock_service.taak_aanmaken.return_value = {
            "_links": {"self": {"href": "http://core/taak/1"}},
        }
        MockMORCoreService.return_value = mock_service

        batch = self.service.aanmaken(self.taken)
        verstuur_batch_naar_mor_core(batch["batch_uuid"])

        self.assertEqual(mock_service.taak_aanmaken.call_count, 2)
        self.assertIsNone(self.service.ophalen(batch["batch_uuid"]))

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
        call_kwargs = mock_service.taak_aanmaken.call_args_list[0]
        self.assertEqual(call_kwargs[1]["titel"], "Taak A")

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

    @patch("apps.main.tasks.MORCoreService")
    def test_noop_als_batch_niet_bestaat(self, MockMORCoreService):
        from apps.main.tasks import verstuur_batch_naar_mor_core

        mock_service = MagicMock()
        MockMORCoreService.return_value = mock_service

        verstuur_batch_naar_mor_core("niet-bestaand-uuid")

        mock_service.taak_aanmaken.assert_not_called()

    @patch("apps.main.tasks.MORCoreService")
    def test_alle_cancelled_verstuurt_niks(self, MockMORCoreService):
        from apps.main.tasks import verstuur_batch_naar_mor_core

        mock_service = MagicMock()
        MockMORCoreService.return_value = mock_service

        batch = self.service.aanmaken(self.taken)
        self.service.annuleer_taak(batch["batch_uuid"], "aaa")  # cascades to bbb
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

        # Second call (taak B) should have resolved parent URL
        second_call_kwargs = mock_service.taak_aanmaken.call_args_list[1][1]
        self.assertEqual(
            second_call_kwargs["afhankelijkheid"],
            [{"taakopdracht_url": "http://core/taak/aaa-url"}],
        )

    @patch("apps.main.tasks.MORCoreService")
    def test_verstuur_geeft_batch_uuid_door_aan_taak_aanmaken(self, MockMORCoreService):
        from apps.main.tasks import verstuur_batch_naar_mor_core

        mock_service = MagicMock()
        mock_service.taak_aanmaken.return_value = {
            "_links": {"self": {"href": "http://core/taak/x"}}
        }
        MockMORCoreService.return_value = mock_service

        batch = self.service.aanmaken(self.taken)
        verstuur_batch_naar_mor_core(batch["batch_uuid"])

        # Beide aanroepen krijgen de batch-entry uuid mee als idempotency key.
        ontvangen_uuids = [
            kall.kwargs.get("uuid")
            for kall in mock_service.taak_aanmaken.call_args_list
        ]
        self.assertEqual(ontvangen_uuids, ["aaa", "bbb"])

    @patch("apps.main.tasks.MORCoreService")
    def test_retry_geeft_dezelfde_uuids_door(self, MockMORCoreService):
        from apps.main.tasks import verstuur_batch_naar_mor_core

        # Eerste poging: A slaagt, B faalt.
        mock_service_1 = MagicMock()
        mock_service_1.taak_aanmaken.side_effect = [
            {"_links": {"self": {"href": "http://core/taak/aaa-url"}}},
            Exception("netwerkprobleem"),
        ]

        # Tweede poging (retry): beide moeten dezelfde uuids hergebruiken.
        mock_service_2 = MagicMock()
        mock_service_2.taak_aanmaken.side_effect = [
            {"_links": {"self": {"href": "http://core/taak/aaa-url"}}},
            {"_links": {"self": {"href": "http://core/taak/bbb-url"}}},
        ]

        MockMORCoreService.side_effect = [mock_service_1, mock_service_2]

        batch = self.service.aanmaken(self.taken)

        # Eerste poging valt om door de exception in B.
        with self.assertRaises(Exception):
            verstuur_batch_naar_mor_core(batch["batch_uuid"])

        # Retry vanuit Celery: batch staat nog in cache met dezelfde uuids.
        verstuur_batch_naar_mor_core(batch["batch_uuid"])

        retry_uuids = [
            kall.kwargs.get("uuid")
            for kall in mock_service_2.taak_aanmaken.call_args_list
        ]
        # Beide taken worden met DEZELFDE uuids opnieuw verstuurd, zodat
        # mor-core's idempotency replay de eerste niet dupliceert.
        self.assertEqual(retry_uuids, ["aaa", "bbb"])
