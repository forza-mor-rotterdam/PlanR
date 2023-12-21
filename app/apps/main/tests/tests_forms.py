from apps.main.forms import MeldingAfhandelenForm
from apps.main.models import StandaardExterneOmschrijving
from django.test import TestCase


class MeldingAfhandelenFormTest(TestCase):
    def setUp(self):
        (
            self.standaard_omschrijving,
            _created,
        ) = StandaardExterneOmschrijving.objects.get_or_create(
            titel="Standaard afhandelreden",
            tekst="Deze melding is behandeld. Bedankt voor uw inzet om Rotterdam schoon, heel en veilig te houden.",
        )

    def test_omschrijving_extern_te_lang(self):
        form_data = {
            "omschrijving_extern": "A" * 1001,
            "standaard_omschrijvingen": self.standaard_omschrijving,
        }
        form = MeldingAfhandelenForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_omschrijving_extern_valide(self):
        form_data = {
            "omschrijving_extern": "A" * 500,
            "standaard_omschrijvingen": self.standaard_omschrijving,
        }
        form = MeldingAfhandelenForm(data=form_data)
        print(form.errors)
        self.assertTrue(form.is_valid())
