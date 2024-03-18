import requests_mock
from apps.authenticatie.models import Gebruiker
from apps.main.models import StandaardExterneOmschrijving
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse


class StandaardExterneOmschrijvingTests(TestCase):
    @requests_mock.Mocker()
    def setUp(self, m):
        m.post("http://mock.com/api/v1/gebruiker/", json={}, status_code=200)

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
        m.post("http://mock.com/api/v1/gebruiker/", json={}, status_code=200)
        self.client.force_login(self.user)
        response = self.client.get(reverse("standaard_externe_omschrijving_lijst"))
        self.assertEqual(response.status_code, 200)

    @requests_mock.Mocker()
    def test_standaard_externe_omschrijving_aanmaken_view(self, m):
        m.post("http://mock.com/api/v1/gebruiker/", json={}, status_code=200)
        self.client.force_login(self.user)
        response = self.client.get(reverse("standaard_externe_omschrijving_aanmaken"))
        self.assertEqual(response.status_code, 200)

    @requests_mock.Mocker()
    def test_standaard_externe_omschrijving_aanpassen_view(self, m):
        m.post("http://mock.com/api/v1/gebruiker/", json={}, status_code=200)
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
        self.client.force_login(self.user_without_permissions)
        response = self.client.get(reverse("standaard_externe_omschrijving_lijst"))
        self.assertEqual(response.status_code, 403)

    @requests_mock.Mocker()
    def test_no_permission_standaard_externe_omschrijving_aanmaken_view(self, m):
        m.post("http://mock.com/api/v1/gebruiker/", json={}, status_code=200)
        self.client.force_login(self.user_without_permissions)
        response = self.client.get(reverse("standaard_externe_omschrijving_aanmaken"))
        self.assertEqual(response.status_code, 403)

    # Form submission tests

    @requests_mock.Mocker()
    def test_standaard_externe_omschrijving_aanmaken_valid_form_submission(self, m):
        m.post("http://mock.com/api/v1/gebruiker/", json={}, status_code=200)
        self.client.force_login(self.user)
        data = {"titel": "Test Titel", "tekst": "Test Tekst"}
        response = self.client.post(
            reverse("standaard_externe_omschrijving_aanmaken"), data=data
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("standaard_externe_omschrijving_lijst"))

    @requests_mock.Mocker()
    def test_standaard_externe_omschrijving_aanpassen_valid_form_submission(self, m):
        m.post("http://mock.com/api/v1/gebruiker/", json={}, status_code=200)
        omschrijving = StandaardExterneOmschrijving.objects.create(
            titel="Test Titel", tekst="Test Tekst"
        )
        self.client.force_login(self.user)
        data = {"titel": "Updated Titel", "tekst": "Updated Tekst"}
        response = self.client.post(
            reverse("standaard_externe_omschrijving_aanpassen", args=[omschrijving.pk]),
            data=data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("standaard_externe_omschrijving_lijst"))

    @requests_mock.Mocker()
    def test_standaard_externe_omschrijving_verwijderen_valid_form_submission(self, m):
        m.post("http://mock.com/api/v1/gebruiker/", json={}, status_code=200)
        omschrijving = StandaardExterneOmschrijving.objects.create(
            titel="Test Titel", tekst="Test Tekst"
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
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("standaard_externe_omschrijving_aanmaken"), data={}
        )
        self.assertEqual(response.status_code, 200)

    @requests_mock.Mocker()
    def test_standaard_externe_omschrijving_aanpassen_invalid_form_submission(self, m):
        m.post("http://mock.com/api/v1/gebruiker/", json={}, status_code=200)
        omschrijving = StandaardExterneOmschrijving.objects.create(
            titel="Test Titel", tekst="Test Tekst"
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
        non_existing_instance_id = 999
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(
                "standaard_externe_omschrijving_verwijderen",
                args=[non_existing_instance_id],
            )
        )
        self.assertEqual(response.status_code, 404)
