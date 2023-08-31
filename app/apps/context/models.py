from django.contrib.gis.db import models
from utils.fields import DictJSONField
from utils.models import BasisModel


class Context(BasisModel):
    """
    Profiel model voor Gebruikers
    """

    class TemplateOpties(models.TextChoices):
        STANDAARD = "standaard", "Standaard"
        BENC = "benc", "Begraven & Cremeren"

    naam = models.CharField(max_length=100)
    filters = DictJSONField(default=dict)

    template = models.CharField(
        max_length=50,
        choices=TemplateOpties.choices,
        default=TemplateOpties.STANDAARD,
    )

    def __str__(self):
        return self.naam
