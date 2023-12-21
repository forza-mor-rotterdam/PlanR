from apps.services.meldingen import MeldingenService
from apps.services.onderwerpen import render_onderwerp
from django.contrib.gis.db import models
from utils.fields import DictJSONField, ListJSONField
from utils.models import BasisModel


class Context(BasisModel):
    """
    Profiel model voor Gebruikers
    """

    class TemplateOpties(models.TextChoices):
        STANDAARD = "standaard", "Standaard"
        BENC = "benc", "Begraven & Cremeren"

    naam = models.CharField(max_length=100, unique=True)
    filters = DictJSONField(default=dict)
    kolommen = DictJSONField(default=dict)
    standaard_filters = DictJSONField(default=dict)
    taaktypes = ListJSONField(default=list)

    template = models.CharField(
        max_length=50,
        choices=TemplateOpties.choices,
        default=TemplateOpties.STANDAARD,
    )

    def onderwerpen(self):
        onderwerp_alias_list = (
            MeldingenService().onderwerp_alias_list().get("results", [])
        )
        onderwerpen = [
            render_onderwerp(onderwerp_alias.get("bron_url"), onderwerp_alias.get("pk"))
            for onderwerp_alias in onderwerp_alias_list
            if str(onderwerp_alias.get("pk"))
            in self.standaard_filters.get("pre_onderwerp", [])
        ]
        return onderwerpen

    def taaktype_namen(self):
        taakapplicaties = MeldingenService().taakapplicaties().get("results", [])
        taaktypes = [tt for ta in taakapplicaties for tt in ta.get("taaktypes", [])]
        taaktype_namen = [
            taaktype.get("omschrijving")
            for taaktype in taaktypes
            if taaktype.get("_links", {}).get("self") in self.taaktypes
        ]
        return taaktype_namen

    def __str__(self):
        return self.naam
