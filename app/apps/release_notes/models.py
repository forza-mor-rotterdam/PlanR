import logging
import mimetypes
import os
from os.path import exists

from apps.authenticatie.forms import Gebruiker
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from django.utils import timezone
from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener
from sorl.thumbnail import get_thumbnail
from utils.images import get_upload_path
from utils.models import BasisModel

logger = logging.getLogger(__name__)


class Bijlage(BasisModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    bestand = models.FileField(
        upload_to=get_upload_path, null=False, blank=False, max_length=255
    )
    afbeelding = models.ImageField(
        upload_to=get_upload_path, null=True, blank=True, max_length=255
    )
    afbeelding_verkleind = models.ImageField(
        upload_to=get_upload_path, null=True, blank=True, max_length=255
    )

    mimetype = models.CharField(max_length=30, blank=False, null=False)
    is_afbeelding = models.BooleanField(default=False)

    class BestandPadFout(Exception):
        ...

    class AfbeeldingVersiesAanmakenFout(Exception):
        ...

    def _is_afbeelding(self):
        try:
            Image.open(self.bestand)
        except UnidentifiedImageError:
            return False
        return True

    def _heic_to_jpeg(self, file_field):
        register_heif_opener()

        with Image.open(file_field.path) as image:
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Remove .heic extension and add .jpg
            new_file_name = f"{os.path.splitext(file_field.name)[0]}.jpg"

            image.save(os.path.join(settings.MEDIA_ROOT, new_file_name), "JPEG")

        return new_file_name

    def aanmaken_afbeelding_versies(self):
        mt = mimetypes.guess_type(self.bestand.path, strict=True)

        if exists(self.bestand.path):
            bestand = self.bestand.path
            self.is_afbeelding = self._is_afbeelding()
            if mt:
                self.mimetype = mt[0]
            if self.mimetype == "image/heic":
                bestand = self._heic_to_jpeg(self.bestand)
                self.is_afbeelding = True

            # Dont convert to jpeg if the image is a gif.
            if self.mimetype == "image/gif":
                return
            if self.is_afbeelding:
                try:
                    self.afbeelding_verkleind.name = get_thumbnail(
                        bestand,
                        settings.THUMBNAIL_KLEIN,
                        format="JPEG",
                        quality=99,
                    ).name
                    self.afbeelding.name = get_thumbnail(
                        bestand,
                        settings.THUMBNAIL_STANDAARD,
                        format="JPEG",
                        quality=80,
                    ).name
                except Exception as e:
                    raise Bijlage.AfbeeldingVersiesAanmakenFout(
                        f"aanmaken_afbeelding_versies: get_thumbnail fout: {e}"
                    )
        else:
            raise Bijlage.BestandPadFout(
                f"aanmaken_afbeelding_versies: bestand path bestaat niet, bijlage id: {self.pk}"
            )

    class Meta:
        verbose_name = "Bijlage"
        verbose_name_plural = "Bijlagen"


class ReleaseNote(BasisModel):
    class BerichtTypeOpties(models.TextChoices):
        RELEASE_NOTE = "release_note", "Release note"
        NOTIFICATIE = "notificatie", "Notificatie"

    class NotificatieTypeOpties(models.TextChoices):
        SNACK = "snack", "Snack"
        TOAST = "toast", "Toast"

    class NotificatieNiveauOpties(models.TextChoices):
        INFO = "info", "Informatief"
        WARNING = "warning", "Waarschuwing"
        ERROR = "error", "Foutmelding"

    titel = models.CharField(max_length=255)
    korte_beschrijving = models.TextField(blank=True, null=True, max_length=500)
    beschrijving = models.TextField(blank=True, null=True, max_length=5000)
    bericht_type = models.CharField(
        max_length=50,
        choices=BerichtTypeOpties.choices,
        default=BerichtTypeOpties.RELEASE_NOTE,
    )
    notificatie_type = models.CharField(
        max_length=50,
        choices=NotificatieTypeOpties.choices,
        default=NotificatieTypeOpties.SNACK,
    )
    notificatie_niveau = models.CharField(
        max_length=50,
        choices=NotificatieNiveauOpties.choices,
        default=NotificatieNiveauOpties.INFO,
    )
    publicatie_datum = models.DateTimeField(null=False, blank=False)
    einde_publicatie_datum = models.DateTimeField(blank=True, null=True)
    bijlagen = GenericRelation(Bijlage)
    versie = models.CharField(max_length=20, blank=True, null=True)
    link_titel = models.CharField(max_length=20, blank=True, null=True)
    link_url = models.URLField(blank=True, null=True)
    bekeken_door_gebruikers = models.ManyToManyField(
        Gebruiker, blank=True, related_name="bekeken_release_notes"
    )
    verwijderbaar = models.BooleanField(
        default=True,
    )
    toast_miliseconden_zichtbaar = models.PositiveSmallIntegerField(
        default=6000,
    )

    def has_beschrijving(self):
        soup = BeautifulSoup(self.beschrijving, features="html.parser")
        return soup.text.strip()

    # def publicatie_datum_timestamp

    def is_published(self):
        """
        Check if the release note is valid, i.e., not in the future and not older than five weeks.
        """
        five_weeks_ago = timezone.now() - timezone.timedelta(weeks=5)
        return not (
            self.publicatie_datum > timezone.now()
            or self.publicatie_datum < five_weeks_ago
        )

    def is_unwatched_by_user(self, user):
        """
        Check if the release note is unwatched by the user and meets the specified conditions.
        """

        return not self.bekeken_door_gebruikers.filter(pk=user.pk).exists()

    @staticmethod
    def count_unwatched(user):
        """
        Count the number of unwatched release notes for the user.
        """
        return sum(
            release_note.is_published() and release_note.is_unwatched_by_user(user)
            for release_note in ReleaseNote.objects.filter(
                bericht_type=ReleaseNote.BerichtTypeOpties.RELEASE_NOTE
            )
        )

    def __str__(self):
        if self.titel and self.aangemaakt_op:
            formatted_date = self.aangemaakt_op.strftime("%d-%m-%Y %H:%M:%S")
            return f"{self.titel} - {formatted_date}"
        return self.id

    def clean(self):
        data = self.beschrijving

        soup = BeautifulSoup(data, features="html.parser")

        for tag in [t for t in soup.find_all(True) if t.name in ("body", "html")]:
            tag.unwrap()

        unwanted_tags = [
            tag
            for tag in soup.find_all(True)
            if tag.name
            not in [
                "strong",
                "em",
                "b",
                "p",
                "i",
                "u",
                "strike",
                "ol",
                "ul",
                "li",
                "blockquote",
                "div",
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6",
                "pre",
                "address",
                "a",
                "img",
                "span",
                "iframe",
                "video",
            ]
        ]

        for tag in unwanted_tags:
            tag.decompose()

        # remove attributes starting with 'on'
        for tag in soup.find_all(True):
            tag.attrs = {
                k: v
                for k, v in tag.attrs.items()
                if not k.startswith("on")
                and k not in ["srcdoc"]
                and "javascript:" not in v
            }

        self.beschrijving = str(soup)

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.id and self.publicatie_datum > timezone.now():
            self.bekeken_door_gebruikers.clear()
        return super().save(*args, **kwargs)
