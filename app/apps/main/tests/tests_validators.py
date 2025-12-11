from apps.main.validators import validate_taakvolgorde
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase


class TestValidateTaakvolgorde(SimpleTestCase):
    def test_taak_parents_geen_json(self):
        """
        De parents waarde van taak 1 bevat geen json
        """
        taken = [
            {
                "uuid": "1",
                "parents": "geen json",
            },
            {
                "uuid": "2",
                "parents": '["1"]',
            },
        ]
        with self.assertRaisesMessage(
            ValidationError, "de parent waarde van een taak bevat geen json"
        ):
            validate_taakvolgorde(taken)

    def test_taak_ids_niet_uniek(self):
        """
        Taak id 1, komt twee keer voor
        """
        taken = [
            {
                "uuid": "1",
                "parents": '["4"]',
            },
            {
                "uuid": "1",
                "parents": '["1"]',
            },
        ]
        with self.assertRaisesMessage(ValidationError, "taak id's zijn niet uniek"):
            validate_taakvolgorde(taken)

    def test_relatie_overeenkomstige_ouder(self):
        """
        Taak 4 is afhankelijk van 3 en 2. En taak 3 is ook afhankelijk van 2
        """
        taken = [
            {
                "uuid": "1",
                "parents": "[]",
            },
            {
                "uuid": "2",
                "parents": '["1"]',
            },
            {
                "uuid": "3",
                "parents": '["2"]',
            },
            {
                "uuid": "4",
                "parents": '["3", "2"]',
            },
            {
                "uuid": "5",
                "parents": '["4", "6"]',
            },
            {
                "uuid": "6",
                "parents": "[]",
            },
        ]
        with self.assertRaisesMessage(
            ValidationError, "relatie gevonden die een overeenkomstige ouder hebben: 4"
        ):
            validate_taakvolgorde(taken)

    def test_taak_direct_afhankelijk_van_zichzelf(self):
        """
        Taak 2 afhankelijk van taak 2
        """
        taken = [
            {
                "uuid": "1",
                "parents": '["4"]',
            },
            {
                "uuid": "2",
                "parents": '["2","1"]',
            },
        ]
        with self.assertRaisesMessage(
            ValidationError, 'taak verwijst naar zichzelf: 2 in ["2", "1"]'
        ):
            validate_taakvolgorde(taken)

    def test_taken_relatie_loop(self):
        """
        Taak 1 heeft als ouders 4, 3, 2, 1
        """
        taken = [
            {
                "uuid": "1",
                "parents": '["4"]',
            },
            {
                "uuid": "2",
                "parents": '["1"]',
            },
            {
                "uuid": "3",
                "parents": '["2"]',
            },
            {
                "uuid": "4",
                "parents": '["3"]',
            },
            {
                "uuid": "5",
                "parents": '["4"]',
            },
        ]
        with self.assertRaisesMessage(
            ValidationError, "taak komt voor in 1 of meer van z'n"
        ):
            validate_taakvolgorde(taken)

    def test_correcte_relaties(self):
        """
        Correcte relaties
        """
        taken = [
            {
                "uuid": "1",
                "parents": "[]",
            },
            {
                "uuid": "2",
                "parents": '["1"]',
            },
            {
                "uuid": "3",
                "parents": '["2"]',
            },
            {
                "uuid": "4",
                "parents": '["3"]',
            },
            {
                "uuid": "5",
                "parents": '["4", "6"]',
            },
            {
                "uuid": "6",
                "parents": "[]",
            },
            {
                "uuid": "7",
                "parents": '["3"]',
            },
            {
                "uuid": "8",
                "parents": '["1"]',
            },
            {
                "uuid": "9",
                "parents": '["1"]',
            },
        ]
        self.assertEquals(len(taken), len(validate_taakvolgorde(taken)))
