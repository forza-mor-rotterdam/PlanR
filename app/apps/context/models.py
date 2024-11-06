import json

from apps.main.services import (
    MORCoreService,
    OnderwerpenService,
    TaakRService,
    render_onderwerp,
)
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
            MORCoreService().onderwerp_alias_list(force_cache=False).get("results", [])
        )
        onderwerpen = [
            render_onderwerp(
                onderwerp_alias.get("bron_url"),
                onderwerp_alias.get("pk"),
                force_cache=False,
            )
            for onderwerp_alias in onderwerp_alias_list
            if str(onderwerp_alias.get("pk"))
            in self.standaard_filters.get("pre_onderwerp", [])
        ]
        return onderwerpen

    def onderwerp_opties_gegroepeerd(self):
        onderwerp_alias_list = (
            MORCoreService().onderwerp_alias_list(force_cache=False).get("results", [])
        )
        onderwerpen_data = [
            [
                str(onderwerp_alias.get("pk")),
                OnderwerpenService().get_onderwerp(
                    onderwerp_alias.get("bron_url"), force_cache=False
                ),
            ]
            for onderwerp_alias in onderwerp_alias_list
            if str(onderwerp_alias.get("pk"))
            in self.standaard_filters.get("pre_onderwerp", [])
        ]
        onderwerpen_data = [
            [onderwerp[1].get("group_uuid"), onderwerp]
            for onderwerp in onderwerpen_data
        ]
        groepen = [
            [
                OnderwerpenService()
                .get_groep(group_uuid, force_cache=False)
                .get("name", ""),
                [
                    [onderwerp[1][0], {"label": onderwerp[1][1].get("name")}]
                    for onderwerp in onderwerpen_data
                    if onderwerp[1][1].get("group_uuid") == group_uuid
                ],
            ]
            for group_uuid in list(set([groep[0] for groep in onderwerpen_data]))
        ]
        return groepen

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
        taaktypes = TaakRService().get_taaktypes(force_cache=False)
        taaktype_namen = [
            taaktype.get("omschrijving")
            for taaktype in taaktypes
            if taaktype.get("_links", {}).get("taakapplicatie_taaktype_url")
            in self.taaktypes
        ]
        return taaktype_namen

    def __str__(self):
        return self.naam

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Rollen"
        ordering = ["naam"]
