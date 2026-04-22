from unittest.mock import MagicMock, patch

from django.test import TestCase

from apps.main.services import MORCoreService


class MORCoreServiceVernietigingslijstTest(TestCase):
    """Verifieert dat get_vernietigingslijst de juiste SDK-aanroepen doet.

    We omzeilen __init__ omdat die Instelling.actieve_instelling() ophaalt,
    wat voor deze test niet relevant is - we testen puur de URL-constructie
    en het envelopes-doorgeef-pad.
    """

    def test_roept_stel_url_samen_met_juiste_segmenten_aan(self):
        service = MORCoreService.__new__(MORCoreService)

        fake_response = MagicMock()
        fake_response.elapsed.total_seconds.return_value = 0.01
        fake_response.content = b"{}"

        verwachte_envelope = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": [],
        }

        with patch.object(
            MORCoreService,
            "stel_url_samen",
            return_value="http://core.mor.local:8002/api/v1/vernietigingslijst/signaal",
        ) as stel, patch.object(
            MORCoreService, "do_request", return_value=fake_response
        ) as doe, patch.object(
            MORCoreService, "naar_json", return_value=verwachte_envelope
        ):
            resultaat = service.get_vernietigingslijst()

        stel.assert_called_once_with("vernietigingslijst", "signaal")
        # URL die do_request krijgt moet op "?" eindigen als er geen query_string is.
        doe.assert_called_once()
        _, kwargs = doe.call_args
        aangeroepen_url = doe.call_args.args[0] if doe.call_args.args else kwargs.get("url")
        self.assertIn("/api/v1/vernietigingslijst/signaal", aangeroepen_url)
        self.assertEqual(resultaat, verwachte_envelope)

    def test_geeft_dict_response_ongewijzigd_door(self):
        """Als do_request een dict retourneert (error-pad), wordt die direct teruggegeven."""
        service = MORCoreService.__new__(MORCoreService)
        fout_envelope = {"error": "boom"}

        with patch.object(
            MORCoreService,
            "stel_url_samen",
            return_value="http://core.mor.local:8002/api/v1/vernietigingslijst/signaal",
        ), patch.object(
            MORCoreService, "do_request", return_value=fout_envelope
        ):
            resultaat = service.get_vernietigingslijst()

        self.assertEqual(resultaat, fout_envelope)
