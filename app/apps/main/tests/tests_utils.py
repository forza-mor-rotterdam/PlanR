from apps.main.utils import melding_taken, snake_case
from django.test import SimpleTestCase


class TestUtils(SimpleTestCase):
    def test_snake_case(self):
        """
        text_list only when an reopens when unhappy string
        """
        string_in = "Mock data mock mock"
        string_out = "mock_data_mock_mock"

        self.assertEqual(snake_case(string_in), string_out)


def _maak_taakopdracht(titel, self_url, afhankelijkheid=None, verwijderd_op=None, uitgezet_op=None):
    return {
        "titel": titel,
        "uuid": self_url.split("/")[-2] if "/" in self_url else self_url,
        "_links": {"self": self_url},
        "afhankelijkheid": afhankelijkheid or [],
        "verwijderd_op": verwijderd_op,
        "uitgezet_op": uitgezet_op,
        "status": {"naam": "nieuw"},
        "resolutie": None,
    }


class TestMeldingTakenWachttekst(SimpleTestCase):
    def test_geen_afhankelijkheden_geen_wachttekst(self):
        melding = {
            "taakopdrachten_voor_melding": [
                _maak_taakopdracht("Taak A", "http://api/taakopdracht/aaa/"),
            ]
        }
        result = melding_taken(melding)
        taak = result["niet_verwijderde_taken"][0]
        self.assertEqual(taak["afhankelijkheid_titels"], [])
        self.assertEqual(taak["afhankelijkheid_wachttekst"], "")

    def test_een_afhankelijkheid_enkelvoud(self):
        melding = {
            "taakopdrachten_voor_melding": [
                _maak_taakopdracht("Taak A", "http://api/taakopdracht/aaa/"),
                _maak_taakopdracht(
                    "Taak B",
                    "http://api/taakopdracht/bbb/",
                    afhankelijkheid=[{"taakopdracht_url": "http://api/taakopdracht/aaa/"}],
                ),
            ]
        }
        result = melding_taken(melding)
        taak_b = next(t for t in result["niet_verwijderde_taken"] if t["titel"] == "Taak B")
        self.assertEqual(taak_b["afhankelijkheid_titels"], ["Taak A"])
        self.assertEqual(
            taak_b["afhankelijkheid_wachttekst"],
            'Wacht tot de taak "Taak A" is uitgevoerd',
        )

    def test_twee_afhankelijkheden_meervoud(self):
        melding = {
            "taakopdrachten_voor_melding": [
                _maak_taakopdracht("Taak A", "http://api/taakopdracht/aaa/"),
                _maak_taakopdracht("Taak B", "http://api/taakopdracht/bbb/"),
                _maak_taakopdracht(
                    "Taak C",
                    "http://api/taakopdracht/ccc/",
                    afhankelijkheid=[
                        {"taakopdracht_url": "http://api/taakopdracht/aaa/"},
                        {"taakopdracht_url": "http://api/taakopdracht/bbb/"},
                    ],
                ),
            ]
        }
        result = melding_taken(melding)
        taak_c = next(t for t in result["niet_verwijderde_taken"] if t["titel"] == "Taak C")
        self.assertEqual(taak_c["afhankelijkheid_titels"], ["Taak A", "Taak B"])
        self.assertEqual(
            taak_c["afhankelijkheid_wachttekst"],
            'Wacht tot de taken "Taak A" en "Taak B" zijn uitgevoerd',
        )

    def test_onbekende_afhankelijkheid_url_wordt_overgeslagen(self):
        melding = {
            "taakopdrachten_voor_melding": [
                _maak_taakopdracht(
                    "Taak A",
                    "http://api/taakopdracht/aaa/",
                    afhankelijkheid=[{"taakopdracht_url": "http://api/taakopdracht/onbekend/"}],
                ),
            ]
        }
        result = melding_taken(melding)
        taak = result["niet_verwijderde_taken"][0]
        self.assertEqual(taak["afhankelijkheid_titels"], [])
        self.assertEqual(taak["afhankelijkheid_wachttekst"], "")
