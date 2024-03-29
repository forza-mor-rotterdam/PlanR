from apps.main import models
from apps.main.forms import (
    StandaardExterneOmschrijvingAanpassenForm,
    TaaktypeCategorieAanpassenForm,
)
from apps.main.utils import truncate_tekst
from django.contrib import admin


class StandaardExterneOmschrijvingAdmin(admin.ModelAdmin):
    def korte_tekst(self, obj):
        return truncate_tekst(obj.tekst)

    list_display = ["titel", "korte_tekst"]
    form = StandaardExterneOmschrijvingAanpassenForm

    fieldsets = (
        (None, {"fields": ["titel", "tekst"]}),
        # ("onderwerpen", {"fields": ["onderwerpen"]})
    )
    search_fields = [
        "titel",
    ]
    ordering = ["titel"]

    korte_tekst.short_description = "Tekst"


class TaaktypeCategorieAdmin(admin.ModelAdmin):
    list_display = ["naam", "taaktype_namen"]
    form = TaaktypeCategorieAanpassenForm

    fieldsets = ((None, {"fields": ["naam", "taaktypes"]}),)
    search_fields = [
        "naam",
    ]
    ordering = ["naam"]

    def taaktype_namen(self, obj):
        return obj.taaktype_namen()

    taaktype_namen.short_description = "Taaktypes"


admin.site.register(
    models.StandaardExterneOmschrijving, StandaardExterneOmschrijvingAdmin
)

admin.site.register(models.TaaktypeCategorie, TaaktypeCategorieAdmin)
