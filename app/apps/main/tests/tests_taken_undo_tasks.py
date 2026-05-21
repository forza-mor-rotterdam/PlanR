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
