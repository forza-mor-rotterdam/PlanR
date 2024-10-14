from django.contrib.gis.db import models
from utils.case_conversions import advanced_camel_to_snake


class TijdsvakQuerySet(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        if self.model.__name__ == "Tijdsvak":
            return qs
        brontype = advanced_camel_to_snake(self.model.__name__)
        return qs.filter(databron__brontype=brontype)

    def create(self, **kwargs):
        brontype = advanced_camel_to_snake(self.model.__name__)
        kwargs.update({"brontype": brontype})
        return super().create(**kwargs)
