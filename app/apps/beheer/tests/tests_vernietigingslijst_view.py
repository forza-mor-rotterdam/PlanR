from unittest.mock import patch
from urllib.parse import parse_qs

from apps.authenticatie.models import Gebruiker
from apps.instellingen.models import Instelling
from django.contrib.auth.models import Permission
from django.test import TestCase


def _lege_envelope(count=0, next_url=None, previous_url=None, results=None):
    return {
        "count": count,
        "next": next_url,
        "previous": previous_url,
        "results": results or [],
    }


def _rij(**overschrijvingen):
    """Standaard envelope-rij met alle velden die de serializer oplevert.

    Overschrijf per test alleen de velden die voor die test relevant zijn.
    """
    standaard = {
        "uuid": "11111111-1111-1111-1111-111111111111",
        "bron_signaal_id": "SIA-42",
        "aangemaakt_op": "2020-01-01T10:00:00Z",
        "afgesloten_op": "2021-05-02T10:00:00Z",
        "resolutie": "opgelost",
        "afhandelreden": None,
        "categorie_selectielijst": "15.3",
        "bewaartermijn": "5 jaar",
        "signaal_te_vernietigen_per": "2026-05-02",
        "signaal_vernietigd_op": None,
        "heeft_fotos": False,
        "fotos_te_vernietigen_per": "2022-05-02",
        "fotos_vernietigd_op": None,
        "heeft_contactgegevens": True,
        "contactgegevens_te_vernietigen_per": "2022-05-02",
        "contactgegevens_vernietigd_op": None,
    }
    standaard.update(overschrijvingen)
    return standaard


def _vraag_sdk_op(mock_service_klasse):
    """Geef het query_string-argument terug waarmee get_vernietigingslijst is aangeroepen."""
    instantie = mock_service_klasse.return_value
    instantie.get_vernietigingslijst.assert_called_once()
    _args, kwargs = instantie.get_vernietigingslijst.call_args
    # De view roept hij aan met query_string=<string>.
    assert "query_string" in kwargs, f"query_string niet meegegeven: kwargs={kwargs}"
    return kwargs["query_string"]


class VernietigingslijstViewTests(TestCase):
    URL = "/beheer/vernietigingslijst/"

    def setUp(self):
        # MORCoreService.__init__ leest Instelling.actieve_instelling() — in deze
        # tests patchen we de hele klasse weg, maar een Instelling-rij moet
        # toch bestaan om base_view/middleware te laten werken.
        Instelling.objects.create(mor_core_basis_url="http://mock.com")

        self.gebruiker_met_recht = Gebruiker.objects.create_user(
            email="beheerder@test.nl", password="testpassword"
        )
        self.gebruiker_zonder_recht = Gebruiker.objects.create_user(
            email="geenrecht@test.nl", password="testpassword"
        )
        permissie = Permission.objects.get(codename="beheer_bekijken")
        self.gebruiker_met_recht.user_permissions.add(permissie)

    # --- Autorisatie ---

    @patch("apps.beheer.views.MORCoreService")
    def test_geen_toegang_zonder_permissie(self, mock_service_klasse):
        self.client.force_login(self.gebruiker_zonder_recht)
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 302)
        mock_service_klasse.return_value.get_vernietigingslijst.assert_not_called()

    # --- Happy path ---

    @patch("apps.beheer.views.MORCoreService")
    def test_met_permissie_rendert_tabel(self, mock_service_klasse):
        mock_service_klasse.return_value.get_vernietigingslijst.return_value = (
            _lege_envelope(
                count=2,
                results=[
                    _rij(uuid="aaa", bron_signaal_id="SIA-1"),
                    _rij(uuid="bbb", bron_signaal_id="SIA-2"),
                ],
            )
        )
        self.client.force_login(self.gebruiker_met_recht)

        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, 200)
        inhoud = response.content.decode("utf-8")
        self.assertIn("Meldingnummer", inhoud)
        self.assertIn("SIA-1", inhoud)
        self.assertIn("SIA-2", inhoud)
        self.assertIn("Aantal: 2", inhoud)
        # Dutch-geformatteerde datum: "01-01-2020" voor aangemaakt_op 2020-01-01.
        self.assertIn("01-01-2020", inhoud)

    # --- SDK-aanroep: juiste limit / offset / ordering ---

    @patch("apps.beheer.views.MORCoreService")
    def test_eerste_pagina_stuurt_limit_25_offset_0(self, mock_service_klasse):
        mock_service_klasse.return_value.get_vernietigingslijst.return_value = (
            _lege_envelope()
        )
        self.client.force_login(self.gebruiker_met_recht)

        self.client.get(self.URL)

        query_string = _vraag_sdk_op(mock_service_klasse)
        params = parse_qs(query_string)
        self.assertEqual(params, {
            "limit": ["25"],
            "offset": ["0"],
            "ordering": ["signaal_te_vernietigen_per"],
        })

    @patch("apps.beheer.views.MORCoreService")
    def test_pagina_3_stuurt_offset_50(self, mock_service_klasse):
        mock_service_klasse.return_value.get_vernietigingslijst.return_value = (
            _lege_envelope()
        )
        self.client.force_login(self.gebruiker_met_recht)

        self.client.get(f"{self.URL}?page=3")

        params = parse_qs(_vraag_sdk_op(mock_service_klasse))
        self.assertEqual(params["limit"], ["25"])
        self.assertEqual(params["offset"], ["50"])

    # --- Hardening van page-parameter ---

    @patch("apps.beheer.views.MORCoreService")
    def test_ongeldig_page_param_valt_terug_op_1(self, mock_service_klasse):
        mock_service_klasse.return_value.get_vernietigingslijst.return_value = (
            _lege_envelope()
        )
        self.client.force_login(self.gebruiker_met_recht)

        response = self.client.get(f"{self.URL}?page=abc")

        self.assertEqual(response.status_code, 200)
        params = parse_qs(_vraag_sdk_op(mock_service_klasse))
        self.assertEqual(params["offset"], ["0"])

    @patch("apps.beheer.views.MORCoreService")
    def test_negatief_page_param_valt_terug_op_1(self, mock_service_klasse):
        mock_service_klasse.return_value.get_vernietigingslijst.return_value = (
            _lege_envelope()
        )
        self.client.force_login(self.gebruiker_met_recht)

        response = self.client.get(f"{self.URL}?page=-5")

        self.assertEqual(response.status_code, 200)
        params = parse_qs(_vraag_sdk_op(mock_service_klasse))
        self.assertEqual(params["offset"], ["0"])

    # --- Foutafhandeling ---

    @patch("apps.beheer.views.MORCoreService")
    def test_error_envelope_toont_foutmelding(self, mock_service_klasse):
        mock_service_klasse.return_value.get_vernietigingslijst.return_value = {
            "error": "error",
        }
        self.client.force_login(self.gebruiker_met_recht)

        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, 200)
        inhoud = response.content.decode("utf-8")
        self.assertIn("Kon de vernietigingslijst niet ophalen.", inhoud)
        self.assertIn("Geen signalen om te vernietigen.", inhoud)

    @patch("apps.beheer.views.MORCoreService")
    def test_error_envelope_token_error(self, mock_service_klasse):
        # token_error-pad vanuit BasisService: {"error": "token_error", "detail": None}.
        mock_service_klasse.return_value.get_vernietigingslijst.return_value = {
            "error": "token_error",
            "detail": None,
        }
        self.client.force_login(self.gebruiker_met_recht)

        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, 200)
        inhoud = response.content.decode("utf-8")
        self.assertIn("Kon de vernietigingslijst niet ophalen.", inhoud)
        self.assertIn("Geen signalen om te vernietigen.", inhoud)

    # --- n.v.t.-renderen ---

    @patch("apps.beheer.views.MORCoreService")
    def test_heeft_fotos_false_toont_nvt(self, mock_service_klasse):
        mock_service_klasse.return_value.get_vernietigingslijst.return_value = (
            _lege_envelope(
                count=1,
                results=[_rij(
                    heeft_fotos=False,
                    fotos_te_vernietigen_per="2030-06-15",
                )],
            )
        )
        self.client.force_login(self.gebruiker_met_recht)

        response = self.client.get(self.URL)

        inhoud = response.content.decode("utf-8")
        self.assertIn("n.v.t.", inhoud)
        # De retention-datum hoort juist NIET te verschijnen voor foto's
        # als er geen foto's zijn. 15-06-2030 is de Dutch-geformatteerde
        # weergave van fotos_te_vernietigen_per uit de rij hierboven.
        self.assertNotIn("15-06-2030", inhoud)

    @patch("apps.beheer.views.MORCoreService")
    def test_heeft_contactgegevens_false_toont_nvt(self, mock_service_klasse):
        mock_service_klasse.return_value.get_vernietigingslijst.return_value = (
            _lege_envelope(
                count=1,
                results=[_rij(
                    heeft_contactgegevens=False,
                    contactgegevens_te_vernietigen_per="2030-06-15",
                )],
            )
        )
        self.client.force_login(self.gebruiker_met_recht)

        response = self.client.get(self.URL)

        inhoud = response.content.decode("utf-8")
        self.assertIn("n.v.t.", inhoud)
        self.assertNotIn("15-06-2030", inhoud)

    # --- Prev/Next links ---

    @patch("apps.beheer.views.MORCoreService")
    def test_vorige_link_ontbreekt_op_eerste_pagina(self, mock_service_klasse):
        mock_service_klasse.return_value.get_vernietigingslijst.return_value = (
            _lege_envelope(
                count=100,
                next_url="http://core/api/v1/vernietigingslijst/signaal/?limit=25&offset=25",
                previous_url=None,
                results=[_rij()],
            )
        )
        self.client.force_login(self.gebruiker_met_recht)

        response = self.client.get(self.URL)

        inhoud = response.content.decode("utf-8")
        self.assertNotIn("Vorige", inhoud)
        self.assertIn("Volgende", inhoud)

    @patch("apps.beheer.views.MORCoreService")
    def test_volgende_link_ontbreekt_op_laatste_pagina(self, mock_service_klasse):
        mock_service_klasse.return_value.get_vernietigingslijst.return_value = (
            _lege_envelope(
                count=30,
                next_url=None,
                previous_url="http://core/api/v1/vernietigingslijst/signaal/?limit=25&offset=0",
                results=[_rij()],
            )
        )
        self.client.force_login(self.gebruiker_met_recht)

        response = self.client.get(f"{self.URL}?page=2")

        inhoud = response.content.decode("utf-8")
        self.assertIn("Vorige", inhoud)
        self.assertNotIn("Volgende", inhoud)

    # --- Tombstone weergave ---

    @patch("apps.beheer.views.MORCoreService")
    def test_tombstone_rij_toont_vernietigd_op(self, mock_service_klasse):
        mock_service_klasse.return_value.get_vernietigingslijst.return_value = (
            _lege_envelope(
                count=1,
                results=[_rij(
                    signaal_vernietigd_op="2026-04-20T12:00:00Z",
                )],
            )
        )
        self.client.force_login(self.gebruiker_met_recht)

        response = self.client.get(self.URL)

        inhoud = response.content.decode("utf-8")
        self.assertIn("20-04-2026", inhoud)
