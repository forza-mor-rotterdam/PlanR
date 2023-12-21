from apps.main.forms import MeldingAfhandelenForm
from django.test import TestCase


class MeldingAfhandelenFormTest(TestCase):
    def test_omschrijving_extern_te_lang(self):
        form_data = {
            "omschrijving_extern": "A" * 1001,
        }
        form = MeldingAfhandelenForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_omschrijving_extern_valide(self):
        form_data = {
            "omschrijving_extern": "A" * 500,
        }
        form = MeldingAfhandelenForm(data=form_data)
        self.assertTrue(form.is_valid())
