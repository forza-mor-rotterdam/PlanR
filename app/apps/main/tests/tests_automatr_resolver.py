from apps.main.models import (
    MeldingAfhandelreden,
    StandaardExterneOmschrijving,
    resolve_automatr_settings_batch,
)
from django.test import TestCase


class ResolveSettingsBatchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.reden = MeldingAfhandelreden.objects.create(reden="niet_voor_ons")
        cls.seo_haven = StandaardExterneOmschrijving.objects.create(
            titel="Havenbedrijf Rotterdam",
            tekst="We hebben de melding doorgestuurd naar het Havenbedrijf.",
            zichtbaarheid="niet_opgelost",
            reden=cls.reden,
        )
        cls.seo_other = StandaardExterneOmschrijving.objects.create(
            titel="Verlichting gerepareerd",
            tekst="We hebben de verlichting gerepareerd.",
            zichtbaarheid="opgelost",
        )

    def test_empty_input_returns_empty_list_and_zero_queries(self):
        with self.assertNumQueries(0):
            self.assertEqual(resolve_automatr_settings_batch([]), [])

    def test_none_settings_passes_through_with_zero_queries(self):
        with self.assertNumQueries(0):
            self.assertEqual(resolve_automatr_settings_batch([None]), [None])

    def test_non_list_settings_passes_through(self):
        with self.assertNumQueries(0):
            self.assertEqual(resolve_automatr_settings_batch([{}]), [{}])

    def test_batch_without_omschrijving_id_is_returned_unchanged_zero_queries(self):
        # Shape of `taak_aanmaken_bij_onderwerp` variants — no omschrijving_id.
        taak_aanmaken_settings = [
            {
                "onderwerp": {"url": "http://example.test/x/", "questions": []},
                "taakopdrachten": [
                    {"bericht": "Deze taak is automatisch aangemaakt", "taaktype": "http://t.test/a/"}
                ],
            }
        ]
        with self.assertNumQueries(0):
            result = resolve_automatr_settings_batch([taak_aanmaken_settings])
        self.assertEqual(result, [taak_aanmaken_settings])

    def test_valid_id_resolves_to_tekst_and_strips_id(self):
        settings = [
            {
                "resolutie": "niet_opgelost",
                "afhandelreden": "niet_voor_ons",
                "omschrijving_id": self.seo_haven.id,
                "taakapplicatie_taaktype_url": "http://externr.test/tt/1/",
            }
        ]
        result = resolve_automatr_settings_batch([settings])
        self.assertEqual(
            result,
            [[
                {
                    "resolutie": "niet_opgelost",
                    "afhandelreden": "niet_voor_ons",
                    "omschrijving_extern": self.seo_haven.tekst,
                    "taakapplicatie_taaktype_url": "http://externr.test/tt/1/",
                }
            ]],
        )
        # omschrijving_id key is gone; omschrijving_extern is present; no extras.
        self.assertNotIn("omschrijving_id", result[0][0])

    def test_multiple_settings_resolve_in_single_query(self):
        settings_a = [{"omschrijving_id": self.seo_haven.id, "resolutie": "niet_opgelost"}]
        settings_b = [{"omschrijving_id": self.seo_other.id, "resolutie": "opgelost"}]
        settings_c = [{"omschrijving_id": self.seo_haven.id, "resolutie": "niet_opgelost"}]
        with self.assertNumQueries(1):
            result = resolve_automatr_settings_batch([settings_a, settings_b, settings_c])
        self.assertEqual(result[0][0]["omschrijving_extern"], self.seo_haven.tekst)
        self.assertEqual(result[1][0]["omschrijving_extern"], self.seo_other.tekst)
        self.assertEqual(result[2][0]["omschrijving_extern"], self.seo_haven.tekst)

    def test_null_omschrijving_id_drops_variant(self):
        settings = [{"omschrijving_id": None, "resolutie": "opgelost"}]
        with self.assertNumQueries(0):
            self.assertEqual(resolve_automatr_settings_batch([settings]), [[]])

    def test_string_omschrijving_id_drops_variant(self):
        settings = [{"omschrijving_id": "4", "resolutie": "opgelost"}]
        with self.assertNumQueries(0):
            self.assertEqual(resolve_automatr_settings_batch([settings]), [[]])

    def test_nonexistent_omschrijving_id_drops_variant(self):
        settings = [{"omschrijving_id": 99999, "resolutie": "opgelost"}]
        with self.assertNumQueries(1):
            result = resolve_automatr_settings_batch([settings])
        self.assertEqual(result, [[]])

    def test_variant_that_is_not_a_dict_passes_through(self):
        settings = ["unexpected string", 42]
        self.assertEqual(resolve_automatr_settings_batch([settings]), [["unexpected string", 42]])

    def test_good_and_bad_variants_in_same_settings_list(self):
        settings = [
            {"omschrijving_id": self.seo_haven.id, "resolutie": "niet_opgelost"},
            {"omschrijving_id": 99999, "resolutie": "niet_opgelost"},  # dropped
            {"omschrijving_id": None, "resolutie": "niet_opgelost"},    # dropped
        ]
        result = resolve_automatr_settings_batch([settings])[0]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["omschrijving_extern"], self.seo_haven.tekst)

    def test_mixed_batch_with_no_resolvable_ids_zero_queries(self):
        # A non-empty batch whose variants either (a) have no `omschrijving_id`
        # key or (b) have a key with a non-int value must NOT trigger the SEO
        # query — `resolve_settings_batch` short-circuits when `ids` is empty.
        # This pins the short-circuit; otherwise it could silently regress
        # into a `WHERE pk IN ()` query on every request during the cutover
        # window (when most rows still carry literal `omschrijving_extern`).
        taak = [{"onderwerp": {}, "taakopdrachten": []}]
        literal = [
            {"omschrijving_extern": "already-a-literal", "resolutie": "opgelost"}
        ]
        bad_type = [{"omschrijving_id": None, "resolutie": "opgelost"}]
        with self.assertNumQueries(0):
            result = resolve_automatr_settings_batch([taak, literal, None, {}, bad_type])
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0], taak)
        self.assertEqual(result[1], literal)
        self.assertIsNone(result[2])
        self.assertEqual(result[3], {})
        self.assertEqual(result[4], [])  # the bad_type variant was dropped
