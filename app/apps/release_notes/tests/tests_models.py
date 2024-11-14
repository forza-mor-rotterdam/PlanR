from apps.release_notes.models import ReleaseNote
from django.test import TestCase
from django.utils import timezone


class ReleaseNoteTest(TestCase):
    def test_beschrijving_strip_attr(self):
        beschrijving_clean = "<p>mock</p>"
        beschrijving_dirty = "<p onMock=\"alert('hi');\">mock</p>"
        release_note = ReleaseNote(
            titel="mock",
            publicatie_datum=timezone.now(),
            beschrijving=beschrijving_dirty,
        )
        release_note.save()
        self.assertEqual(release_note.beschrijving, beschrijving_clean)

    def test_beschrijving_strip_tag_with_content(self):
        beschrijving_clean = "<p>mock</p>"
        beschrijving_dirty = '<p>mock<script>alert("hi");</script></p>'
        release_note = ReleaseNote(
            titel="mock",
            publicatie_datum=timezone.now(),
            beschrijving=beschrijving_dirty,
        )
        release_note.save()
        self.assertEqual(release_note.beschrijving, beschrijving_clean)

    def test_beschrijving_strip_attr_with_js(self):
        beschrijving_clean = "<p>mock</p>"
        beschrijving_dirty = "<p href=\"javascript:alert('hi');\">mock</p>"
        release_note = ReleaseNote(
            titel="mock",
            publicatie_datum=timezone.now(),
            beschrijving=beschrijving_dirty,
        )
        release_note.save()
        self.assertEqual(release_note.beschrijving, beschrijving_clean)
