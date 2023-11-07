from django.db import models
from utils.models import BasisModel


class StandaardExterneOmschrijving(BasisModel):
    titel = models.CharField(max_length=100, unique=True)
    tekst = models.CharField(
        max_length=2000,
        unique=True,
    )

    # def onderwerpen(self):
    #     onderwerp_alias_list = (
    #         MeldingenService().onderwerp_alias_list().get("results", [])
    #     )
    #     onderwerpen = [
    #         render_onderwerp(onderwerp_alias.get("bron_url"), onderwerp_alias.get("pk"))
    #         for onderwerp_alias in onderwerp_alias_list
    #         if str(onderwerp_alias.get("pk"))
    #         in self.standaard_filters.get("pre_onderwerp", [])
    #     ]
    #     return onderwerpen

    class Meta:
        verbose_name = "Standaard externe omschrijving"
        verbose_name_plural = "Standaard externe omschrijvingen"

    def __str__(self):
        return self.titel
