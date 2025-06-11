from apps.main.services import TaakRService
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Q
from utils.fields import ListJSONField
from utils.models import BasisModel

SPECIFICATIE_CACHE_TIMEOUT = 60 * 60 * 24 * 7
STATUS_OPGELOST = "opgelost"
STATUS_NIET_OPGELOST = "niet_opgelost"
STATUS_NIET_OPGELOST_REDENEN = (
    ("reeds_ingepland", "Reeds ingepland", ""),
    ("niet_nu", "Niet nu", ""),
    ("niet_voor_ons", "Niet voor ons", ""),
    ("doen_we_niet", "Doen we niet", ""),
    ("onduidelijk", "Onduidelijk", ""),
)
STATUS_NIET_OPGELOST_REDENEN_TITEL = {
    reden[0]: reden[1] for reden in STATUS_NIET_OPGELOST_REDENEN
}
STATUS_NIET_OPGELOST_REDENEN_OMSCHRIJVING = {
    reden[0]: reden[2] for reden in STATUS_NIET_OPGELOST_REDENEN
}
STATUS_NIET_OPGELOST_REDENEN_CHOICES = [
    (reden[0], reden[1]) for reden in STATUS_NIET_OPGELOST_REDENEN
]
ZICHTBAARHEID = (
    ("altijd", "Altijd tonen"),
    (STATUS_OPGELOST, "Alleen tonen bij opgelost"),
    (STATUS_NIET_OPGELOST, "Alleen tonen bij niet opgelost"),
    ("verbergen", "Verbergen"),
)
ZICHTBAARHEID_TITEL = {
    zichtbaarheid[0]: zichtbaarheid[1] for zichtbaarheid in ZICHTBAARHEID
}
ZICHTBAARHEID_CHOICES = [
    (zichtbaarheid[0], zichtbaarheid[1]) for zichtbaarheid in ZICHTBAARHEID
]


class StandaardExterneOmschrijving(BasisModel):
    titel = models.CharField(max_length=100, unique=True)
    tekst = models.CharField(
        max_length=1000,
    )
    zichtbaarheid = models.CharField(
        max_length=50,
        choices=ZICHTBAARHEID_CHOICES,
        default=ZICHTBAARHEID_CHOICES[0][0],
    )
    reden = models.ForeignKey(
        to="main.MeldingAfhandelreden",
        related_name="standaard_externe_omschrijvingen_voor_melding_afhandelreden",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    specificatie_opties = ArrayField(
        base_field=models.URLField(),
        default=list,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Standaard tekst"
        verbose_name_plural = "Standaard teksten"

    def __str__(self):
        return self.titel

    def save(self, *args, **kwargs):
        if self.zichtbaarheid not in (STATUS_NIET_OPGELOST,):
            self.reden = None
            self.specificatie_opties = []
        if self.reden and not self.reden.specificatie_opties:
            self.specificatie_opties = []
        super().save(*args, **kwargs)


class MeldingAfhandelreden(BasisModel):
    reden = models.CharField(
        max_length=50,
        choices=STATUS_NIET_OPGELOST_REDENEN_CHOICES,
    )
    specificatie_opties = ArrayField(
        base_field=models.URLField(),
        default=list,
        blank=True,
        null=True,
    )

    def get_standaard_externe_omschrijving_lijst(self):
        if self.specificatie_opties:
            return (
                self.standaard_externe_omschrijvingen_voor_melding_afhandelreden.filter(
                    specificatie_opties__isnull=False
                ).exclude(specificatie_opties=[])
            )
        return self.standaard_externe_omschrijvingen_voor_melding_afhandelreden.filter(
            Q(specificatie_opties__isnull=True) | Q(specificatie_opties=[])
        )

    def __str__(self):
        return self.reden


class TaaktypeCategorie(models.Model):
    naam = models.CharField(max_length=100, unique=True)
    taaktypes = ListJSONField(default=list)

    def taaktype_namen(self):
        taaktypes = TaakRService().get_taaktypes()
        taaktype_namen = [
            taaktype.get("omschrijving")
            for taaktype in taaktypes
            if taaktype.get("_links", {}).get("taakapplicatie_taaktype_url")
            in self.taaktypes
        ]
        return taaktype_namen

    def __str__(self):
        return self.naam
