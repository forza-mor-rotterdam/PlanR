from apps.main.models import (
    AutomatRSettings,
    MeldingAfhandelreden,
    StandaardExterneOmschrijving,
)
from django.test import TestCase
from django.urls import reverse


class AutomatRSettingsViewSetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.reden = MeldingAfhandelreden.objects.create(reden="niet_voor_ons")
        cls.seo_haven = StandaardExterneOmschrijving.objects.create(
            titel="Havenbedrijf Rotterdam",
            tekst="We hebben de melding doorgestuurd naar het Havenbedrijf.",
            zichtbaarheid="niet_opgelost",
            reden=cls.reden,
        )
        cls.seo_light = StandaardExterneOmschrijving.objects.create(
            titel="Verlichting gerepareerd",
            tekst="We hebben de verlichting gerepareerd.",
            zichtbaarheid="opgelost",
        )

    def test_list_resolves_omschrijving_id_to_omschrijving_extern(self):
        AutomatRSettings.objects.create(
            name="melding_afhandelen_door_taak",
            settings=[
                {
                    "resolutie": "niet_opgelost",
                    "afhandelreden": "niet_voor_ons",
                    "omschrijving_id": self.seo_haven.id,
                    "taakapplicatie_taaktype_url": "http://externr.test/tt/1/",
                }
            ],
        )
        url = reverse("v1:automatr-settings-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        # PlanR uses LimitOffsetPagination globally (REST_FRAMEWORK.DEFAULT_PAGINATION_CLASS
        # in config/settings.py). AutomatR's `listeners.py:102,114` depends on the
        # envelope key `results` — assert the shape strictly so the contract can't drift.
        self.assertIn("results", body)
        self.assertIn("count", body)
        self.assertEqual(body["count"], 1)
        self.assertEqual(len(body["results"]), 1)
        variant = body["results"][0]["settings"][0]
        self.assertEqual(variant["omschrijving_extern"], self.seo_haven.tekst)
        self.assertNotIn("omschrijving_id", variant)

    def test_list_query_count_is_bounded_independent_of_row_count(self):
        # 3 rows, each referencing a mix of SEOs. The SEO fetch must be a
        # single query across *all* rows.
        AutomatRSettings.objects.create(
            name="melding_afhandelen_door_taak",
            settings=[{"omschrijving_id": self.seo_haven.id, "resolutie": "niet_opgelost"}],
        )
        AutomatRSettings.objects.create(
            name="taak_aanmaken_bij_onderwerp",
            settings=[
                {
                    "onderwerp": {"url": "http://o.test/x/", "questions": []},
                    "taakopdrachten": [
                        {"bericht": "x", "taaktype": "http://t.test/a/"}
                    ],
                }
            ],
        )
        AutomatRSettings.objects.create(
            name="melding_afhandelen_door_taak",
            settings=[{"omschrijving_id": self.seo_light.id, "resolutie": "opgelost"}],
        )
        url = reverse("v1:automatr-settings-list")
        # LimitOffsetPagination issues COUNT(*) + SELECT, plus our one SEO fetch.
        # Key property: 3 is independent of the number of rows — add more rows and
        # it must stay 3.
        with self.assertNumQueries(3):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_query_count_is_two(self):
        row = AutomatRSettings.objects.create(
            name="melding_afhandelen_door_taak",
            settings=[{"omschrijving_id": self.seo_haven.id, "resolutie": "niet_opgelost"}],
        )
        url = reverse("v1:automatr-settings-detail", kwargs={"uuid": row.uuid})
        # No pagination on retrieve: 1 for the detail fetch, 1 for the SEO.
        with self.assertNumQueries(2):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_with_bad_id_drops_that_variant(self):
        row = AutomatRSettings.objects.create(
            name="melding_afhandelen_door_taak",
            settings=[
                {"omschrijving_id": self.seo_haven.id, "resolutie": "niet_opgelost"},
                {"omschrijving_id": 99999, "resolutie": "niet_opgelost"},  # dropped
            ],
        )
        url = reverse("v1:automatr-settings-detail", kwargs={"uuid": row.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        settings = response.json()["settings"]
        self.assertEqual(len(settings), 1)
        self.assertEqual(settings[0]["omschrijving_extern"], self.seo_haven.tekst)

    def test_taak_aanmaken_bij_onderwerp_passes_through_unchanged(self):
        original = [
            {
                "onderwerp": {
                    "url": "http://o.test/x/",
                    "questions": [
                        {"question": "q1", "answers": ["a1"]}
                    ],
                },
                "taakopdrachten": [
                    {"bericht": "auto", "taaktype": "http://t.test/a/"}
                ],
            }
        ]
        row = AutomatRSettings.objects.create(
            name="taak_aanmaken_bij_onderwerp", settings=original
        )
        url = reverse("v1:automatr-settings-detail", kwargs={"uuid": row.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["settings"], original)

    def test_cutover_compat_literal_omschrijving_extern_passes_through_retrieve(self):
        # Pre-cutover shape: literal `omschrijving_extern`, no `omschrijving_id`.
        # Must pass through verbatim so AutomatR keeps working until the row is edited.
        original = [
            {
                "resolutie": "niet_opgelost",
                "afhandelreden": "niet_voor_ons",
                "omschrijving_extern": "Oud letterlijke tekst",
                "taakapplicatie_taaktype_url": "http://externr.test/tt/1/",
            }
        ]
        row = AutomatRSettings.objects.create(
            name="melding_afhandelen_door_taak", settings=original
        )
        url = reverse("v1:automatr-settings-detail", kwargs={"uuid": row.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["settings"], original)

    def test_cutover_compat_literal_omschrijving_extern_passes_through_list(self):
        # Same pre-cutover check, but exercised through the list endpoint's
        # separate override so both code paths are pinned against regression.
        original = [
            {
                "resolutie": "niet_opgelost",
                "afhandelreden": "niet_voor_ons",
                "omschrijving_extern": "Oud letterlijke tekst",
                "taakapplicatie_taaktype_url": "http://externr.test/tt/1/",
            }
        ]
        AutomatRSettings.objects.create(
            name="melding_afhandelen_door_taak", settings=original
        )
        url = reverse("v1:automatr-settings-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["results"][0]["settings"], original)

    def test_resolved_variant_emits_exactly_expected_keys(self):
        row = AutomatRSettings.objects.create(
            name="melding_afhandelen_door_taak",
            settings=[
                {
                    "resolutie": "niet_opgelost",
                    "afhandelreden": "niet_voor_ons",
                    "omschrijving_id": self.seo_haven.id,
                    "taakapplicatie_taaktype_url": "http://externr.test/tt/1/",
                }
            ],
        )
        url = reverse("v1:automatr-settings-detail", kwargs={"uuid": row.uuid})
        response = self.client.get(url)
        variant = response.json()["settings"][0]
        self.assertEqual(
            set(variant.keys()),
            {"resolutie", "afhandelreden", "omschrijving_extern", "taakapplicatie_taaktype_url"},
        )

    def test_list_query_count_skips_seo_fetch_when_no_resolvable_ids(self):
        # During the cutover window, most rows still carry literal
        # `omschrijving_extern` (no `omschrijving_id`). Under those conditions
        # `resolve_settings_batch` short-circuits and issues zero SEO queries.
        # Verify at the HTTP layer: COUNT + SELECT only, no third query.
        AutomatRSettings.objects.create(
            name="melding_afhandelen_door_taak",
            settings=[
                {
                    "resolutie": "niet_opgelost",
                    "afhandelreden": "niet_voor_ons",
                    "omschrijving_extern": "Oud letterlijke tekst",
                    "taakapplicatie_taaktype_url": "http://externr.test/tt/1/",
                }
            ],
        )
        AutomatRSettings.objects.create(
            name="taak_aanmaken_bij_onderwerp",
            settings=[
                {
                    "onderwerp": {"url": "http://o.test/x/", "questions": []},
                    "taakopdrachten": [
                        {"bericht": "x", "taaktype": "http://t.test/a/"}
                    ],
                }
            ],
        )
        url = reverse("v1:automatr-settings-list")
        with self.assertNumQueries(2):  # COUNT + SELECT only
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
