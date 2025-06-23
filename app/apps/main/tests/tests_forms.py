import requests_mock
from apps.instellingen.models import Instelling
from apps.main.forms import MeldingAfhandelenForm
from apps.main.models import (
    STATUS_NIET_OPGELOST_REDENEN_CHOICES,
    MeldingAfhandelreden,
    StandaardExterneOmschrijving,
)
from django.test import TestCase


class MeldingAfhandelenFormTest(TestCase):
    @requests_mock.Mocker()
    def setUp(self, m):
        Instelling.objects.create(
            mor_core_basis_url="http://mock.com",
        )
        self.melding_afhandelreden = MeldingAfhandelreden.objects.create(
            reden=STATUS_NIET_OPGELOST_REDENEN_CHOICES[0][0]
        )

        spec1_url = (
            "http://mock.com/api/v1/specificaties/793797bc-8c90-4437-9894-498190982891/"
        )
        spec2_url = (
            "http://mock.com/api/v1/specificaties/b3ab7f17-17cb-481c-85ed-a43d642ccb0b/"
        )
        spec1 = {
            "_links": {
                "self": {
                    "href": spec1_url,
                }
            },
            "naam": "Spec 1",
            "verwijderd_op": None,
        }
        spec2 = {
            "_links": {
                "self": {
                    "href": spec2_url,
                }
            },
            "naam": "Spec 2",
            "verwijderd_op": None,
        }
        specs_json = {"results": [spec1, spec2]}
        m.get("http://mock.com/api/v1/specificaties/", json=specs_json, status_code=200)
        m.get(spec1_url, json=spec1, status_code=200)
        m.get(spec2_url, json=spec2, status_code=200)
        (
            self.standaard_omschrijving,
            _created,
        ) = StandaardExterneOmschrijving.objects.get_or_create(
            titel="Standaard afhandelreden",
            tekst="Deze melding is behandeld. Bedankt voor uw inzet om Rotterdam schoon, heel en veilig te houden.",
        )

    @requests_mock.Mocker()
    def test_omschrijving_extern_te_lang(self, m):
        m.post("http://mock.com/api/v1/gebruiker/", json={}, status_code=200)
        m.post("http://mock.com/api-token-auth/", json={}, status_code=200)
        form_data = {
            "resolutie": "opgelost",
            "omschrijving_extern": "A" * 1001,
            "standaard_omschrijvingen": self.standaard_omschrijving,
        }
        form = MeldingAfhandelenForm(data=form_data)
        self.assertFalse(form.is_valid())

    @requests_mock.Mocker()
    def test_omschrijving_extern_valide(self, m):
        m.post("http://mock.com/api/v1/gebruiker/", json={}, status_code=200)
        m.post("http://mock.com/api-token-auth/", json={}, status_code=200)
        form_data = {
            "resolutie": "opgelost",
            "omschrijving_extern": "A" * 500,
            "standaard_omschrijvingen": self.standaard_omschrijving,
        }
        form = MeldingAfhandelenForm(data=form_data)
        print(form.errors)
        self.assertTrue(form.is_valid())
