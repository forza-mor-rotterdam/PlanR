from apps.main.forms import MeldingAfhandelenForm
from django.test import TestCase


class MeldingAfhandelenFormTest(TestCase):
    def test_omschrijving_extern_te_lang(self):
        form_data = {
            "omschrijving_extern": "A" * 2001,
        }
        form = MeldingAfhandelenForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_omschrijving_extern_valide(self):
        form_data = {
            "omschrijving_extern": "A" * 1000,
        }
        form = MeldingAfhandelenForm(data=form_data)
        self.assertTrue(form.is_valid())
