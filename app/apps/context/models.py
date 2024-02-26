import json
from urllib.parse import urlparse

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

    @classmethod
    def urgentie_choices(cls):
        return (
            (json.dumps({"urgentie_gte": 0.0}), "Alle meldingen"),
            (json.dumps({"urgentie_gte": 0.5}), "Alleen spoed meldingen"),
            (json.dumps({"urgentie_lt": 0.5}), "Alleen niet spoed meldingen"),
        )

    def urgentie(self):
        urgentie_key_list = [
            k for k in self.standaard_filters.keys() if k.startswith("urgentie_")
        ]
        instance_urgentie = None
        if urgentie_key_list:
            instance_urgentie = json.dumps(
                {urgentie_key_list[0]: self.standaard_filters.get(urgentie_key_list[0])}
            )
        if instance_urgentie in [c[0] for c in Context.urgentie_choices()]:
            return instance_urgentie
        return Context.urgentie_choices()[0][0]

    def urgentie_verbose(self):
        urgentie_key_list = [
            k for k in self.standaard_filters.keys() if k.startswith("urgentie_")
        ]
        instance_urgentie = Context.urgentie_choices()[0][0]
        if urgentie_key_list:
            instance_urgentie = json.dumps(
                {urgentie_key_list[0]: self.standaard_filters.get(urgentie_key_list[0])}
            )
        if instance_urgentie in [c[0] for c in Context.urgentie_choices()]:
            return {c[0]: c[1] for c in Context.urgentie_choices()}.get(
                instance_urgentie
            )
        return Context.urgentie_choices()[0][1]

    def taaktype_namen(self):
        taakapplicaties = MeldingenService().taakapplicaties().get("results", [])
        taaktypes = [tt for ta in taakapplicaties for tt in ta.get("taaktypes", [])]
        taaktype_namen = [
            taaktype.get("omschrijving")
            for taaktype in taaktypes
            if urlparse(taaktype.get("_links", {}).get("self")).path
            in [urlparse(tt).path for tt in self.taaktypes]
        ]
        return taaktype_namen

    def __str__(self):
        return self.naam
