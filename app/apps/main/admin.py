from apps.main import models
from apps.main.forms import StandaardExterneOmschrijvingAanpassenForm
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


admin.site.register(
    models.StandaardExterneOmschrijving, StandaardExterneOmschrijvingAdmin
)
