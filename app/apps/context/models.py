from django.contrib.gis.db import models
from utils.fields import DictJSONField
from utils.models import BasisModel


class Context(BasisModel):
    """
    Profiel model voor Gebruikers
    """

    naam = models.CharField(max_length=100)
    filters = DictJSONField(default=dict)

    def __str__(self):
        return self.naam
