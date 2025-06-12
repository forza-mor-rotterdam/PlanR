import requests_mock
from apps.authenticatie.models import Gebruiker
from apps.instellingen.models import Instelling
from apps.main.models import (
    STATUS_NIET_OPGELOST_REDENEN_CHOICES,
    MeldingAfhandelreden,
    StandaardExterneOmschrijving,
)
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse


class StandaardExterneOmschrijvingTests(TestCase):
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

        m.post("http://mock.com/api/v1/gebruiker/", json={}, status_code=200)
        m.post("http://mock.com/api-token-auth/", json={}, status_code=200)

        self.user = Gebruiker.objects.create_user(
            email="testuser@test.nl", password="testpassword"
        )
        self.user_without_permissions = Gebruiker.objects.create_user(
            email="nopermission@test.nl", password="testpassword"
        )
        permissions = Permission.objects.filter(
            codename__in=[
                "standaard_externe_omschrijving_lijst_bekijken",
                "standaard_externe_omschrijving_aanmaken",
                "standaard_externe_omschrijving_bekijken",
                "standaard_externe_omschrijving_aanpassen",
                "standaard_externe_omschrijving_verwijderen",
            ]
        )
        self.user.user_permissions.add(*permissions)

    # Permission tests

    @requests_mock.Mocker()
    def test_standaard_externe_omschrijving_lijst_view(self, m):
        print("Instelling.objects.count()")
        print(Instelling.objects.count())
        m.post("http://mock.com/api/v1/gebruiker/", json={}, status_code=200)
        m.post("http://mock.com/api-token-auth/", json={}, status_code=200)
        self.client.force_login(self.user)
        response = self.client.get(reverse("standaard_externe_omschrijving_lijst"))
        self.assertEqual(response.status_code, 200)

    @requests_mock.Mocker()
    def test_standaard_externe_omschrijving_aanmaken_view(self, m):
        m.post("http://mock.com/api/v1/gebruiker/", json={}, status_code=200)
        m.post("http://mock.com/api-token-auth/", json={}, status_code=200)
        self.client.force_login(self.user)
        response = self.client.get(reverse("standaard_externe_omschrijving_aanmaken"))
        self.assertEqual(response.status_code, 200)

    @requests_mock.Mocker()
    def test_standaard_externe_omschrijving_aanpassen_view(self, m):
        m.post("http://mock.com/api/v1/gebruiker/", json={}, status_code=200)
        m.post("http://mock.com/api-token-auth/", json={}, status_code=200)
        omschrijving = StandaardExterneOmschrijving.objects.create(
            titel="Test Titel", tekst="Test Tekst"
        )
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("standaard_externe_omschrijving_aanpassen", args=[omschrijving.pk])
        )
        self.assertEqual(response.status_code, 200)

    @requests_mock.Mocker()
    def test_standaard_externe_omschrijving_verwijderen_view(self, m):
        m.post("http://mock.com/api/v1/gebruiker/", json={}, status_code=200)
        m.post("http://mock.com/api-token-auth/", json={}, status_code=200)
        omschrijving = StandaardExterneOmschrijving.objects.create(
            titel="Test Titel", tekst="Test Tekst"
        )
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                "standaard_externe_omschrijving_verwijderen", args=[omschrijving.pk]
            )
        )
        self.assertEqual(response.status_code, 302)
        expected_redirect_url = reverse("standaard_externe_omschrijving_lijst")
        self.assertRedirects(response, expected_redirect_url)

    @requests_mock.Mocker()
    def test_no_permission_standaard_externe_omschrijving_lijst_view(self, m):
        m.post("http://mock.com/api/v1/gebruiker/", json={}, status_code=200)
        m.post("http://mock.com/api-token-auth/", json={}, status_code=200)
        self.client.force_login(self.user_without_permissions)
        response = self.client.get(reverse("standaard_externe_omschrijving_lijst"))
        self.assertEqual(response.status_code, 403)

    @requests_mock.Mocker()
    def test_no_permission_standaard_externe_omschrijving_aanmaken_view(self, m):
        m.post("http://mock.com/api/v1/gebruiker/", json={}, status_code=200)
        m.post("http://mock.com/api-token-auth/", json={}, status_code=200)
        self.client.force_login(self.user_without_permissions)
        response = self.client.get(reverse("standaard_externe_omschrijving_aanmaken"))
        self.assertEqual(response.status_code, 403)

    # Form submission tests

    @requests_mock.Mocker()
    def test_standaard_externe_omschrijving_aanmaken_valid_form_submission(self, m):
        m.post("http://mock.com/api/v1/gebruiker/", json={}, status_code=200)
        m.post("http://mock.com/api-token-auth/", json={}, status_code=200)
        self.client.force_login(self.user)
        data = {
            "titel": "Test Titel",
            "tekst": "Test Tekst",
            "reden": self.melding_afhandelreden,
        }
        response = self.client.post(
            reverse("standaard_externe_omschrijving_aanmaken"), data=data
        )
        self.assertEqual(response.status_code, 200)

    @requests_mock.Mocker()
    def test_standaard_externe_omschrijving_aanpassen_valid_form_submission(self, m):
        m.post("http://mock.com/api/v1/gebruiker/", json={}, status_code=200)
        m.post("http://mock.com/api-token-auth/", json={}, status_code=200)
        omschrijving = StandaardExterneOmschrijving.objects.create(
            titel="Test Titel", tekst="Test Tekst", reden=self.melding_afhandelreden
        )
        self.client.force_login(self.user)
        data = {
            "titel": "Updated Titel",
            "tekst": "Updated Tekst",
            "reden": self.melding_afhandelreden,
        }
        response = self.client.post(
            reverse("standaard_externe_omschrijving_aanpassen", args=[omschrijving.pk]),
            data=data,
        )
        self.assertEqual(response.status_code, 200)

    @requests_mock.Mocker()
    def test_standaard_externe_omschrijving_verwijderen_valid_form_submission(self, m):
        m.post("http://mock.com/api/v1/gebruiker/", json={}, status_code=200)
        m.post("http://mock.com/api-token-auth/", json={}, status_code=200)
        omschrijving = StandaardExterneOmschrijving.objects.create(
            titel="Test Titel", tekst="Test Tekst", reden=self.melding_afhandelreden
        )
        self.client.force_login(self.user)
        response = self.client.post(
            reverse(
                "standaard_externe_omschrijving_verwijderen", args=[omschrijving.pk]
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("standaard_externe_omschrijving_lijst"))

    # Invalid form submission

    @requests_mock.Mocker()
    def test_standaard_externe_omschrijving_aanmaken_invalid_form_submission(self, m):
        m.post("http://mock.com/api/v1/gebruiker/", json={}, status_code=200)
        m.post("http://mock.com/api-token-auth/", json={}, status_code=200)
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("standaard_externe_omschrijving_aanmaken"), data={}
        )
        self.assertEqual(response.status_code, 200)

    @requests_mock.Mocker()
    def test_standaard_externe_omschrijving_aanpassen_invalid_form_submission(self, m):
        m.post("http://mock.com/api/v1/gebruiker/", json={}, status_code=200)
        m.post("http://mock.com/api-token-auth/", json={}, status_code=200)
        omschrijving = StandaardExterneOmschrijving.objects.create(
            titel="Test Titel", tekst="Test Tekst", reden=self.melding_afhandelreden
        )
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("standaard_externe_omschrijving_aanpassen", args=[omschrijving.pk]),
            data={},
        )
        self.assertEqual(response.status_code, 200)

    # Instance does not exist

    @requests_mock.Mocker()
    def test_standaard_externe_omschrijving_verwijderen_instance_does_not_exist(
        self, m
    ):
        m.post("http://mock.com/api/v1/gebruiker/", json={}, status_code=200)
        m.post("http://mock.com/api-token-auth/", json={}, status_code=200)
        non_existing_instance_id = 999
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                "standaard_externe_omschrijving_verwijderen",
                args=[non_existing_instance_id],
            )
        )
        self.assertEqual(response.status_code, 404)
