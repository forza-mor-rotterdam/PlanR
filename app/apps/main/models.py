from apps.services.taakr import TaakRService
from django.db import models
from utils.fields import ListJSONField
from utils.models import BasisModel


class StandaardExterneOmschrijving(BasisModel):
    titel = models.CharField(max_length=100, unique=True)
    tekst = models.CharField(
        max_length=1000,
    )

    class Meta:
        verbose_name = "Standaard tekst"
        verbose_name_plural = "Standaard teksten"

    def __str__(self):
        return self.titel


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
