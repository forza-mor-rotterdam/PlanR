from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings


class ServiceRequestTimeoutTests(TestCase):
    """De mor-api-services client valt zonder expliciete timeout terug op
    timeout=None (geen timeout). Een hangende mor-core call blokkeert dan een
    Celery worker-child voor altijd -> wedged pool -> batches worden nooit
    verstuurd. Deze tests borgen dat elke service een request-timeout meekrijgt.
    """

    def _mock_instelling(self):
        inst = MagicMock()
        inst.mor_core_basis_url = "http://core.mor.local:8002"
        inst.mor_core_gebruiker_email = "a@b.nl"
        inst.mor_core_gebruiker_wachtwoord = "pw"
        inst.mor_core_token_timeout = 0
        inst.onderwerpen_basis_url = "http://onderwerpen.mor.local:8006"
        inst.taakr_basis_url = "http://taakr.mor.local:8009"
        inst.locaties_basis_url = "http://locatieservice.mor.local:8010"
        return inst

    @patch("apps.main.services.Instelling")
    def test_mor_core_service_heeft_request_timeout(self, MockInstelling):
        MockInstelling.actieve_instelling.return_value = self._mock_instelling()
        from apps.main.services import MORCoreService

        self.assertEqual(MORCoreService()._timeout, (10, 30))

    @patch("apps.main.services.Instelling")
    def test_geen_enkele_service_heeft_timeout_none(self, MockInstelling):
        MockInstelling.actieve_instelling.return_value = self._mock_instelling()
        from apps.main.services import (
            LocatieService,
            MORCoreService,
            OnderwerpenService,
            TaakRService,
        )

        for klass in (
            MORCoreService,
            OnderwerpenService,
            TaakRService,
            LocatieService,
        ):
            self.assertIsNotNone(
                klass()._timeout,
                f"{klass.__name__} heeft geen request-timeout (None == oneindig hangen)",
            )

    @override_settings(SERVICE_REQUEST_TIMEOUT=(3, 7))
    @patch("apps.main.services.Instelling")
    def test_timeout_is_configureerbaar_via_settings(self, MockInstelling):
        MockInstelling.actieve_instelling.return_value = self._mock_instelling()
        from apps.main.services import MORCoreService

        self.assertEqual(MORCoreService()._timeout, (3, 7))

    @patch("apps.main.services.Instelling")
    def test_expliciete_timeout_kwarg_overschrijft_default(self, MockInstelling):
        MockInstelling.actieve_instelling.return_value = self._mock_instelling()
        from apps.main.services import MORCoreService

        self.assertEqual(MORCoreService(timeout=(1, 2))._timeout, (1, 2))
