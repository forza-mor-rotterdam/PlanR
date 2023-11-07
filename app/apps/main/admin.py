from apps.main import models
from apps.main.forms import StandaardExterneOmschrijvingAanpassenForm
from django.contrib import admin


class StandaardExterneOmschrijvingAdmin(admin.ModelAdmin):
    def korte_tekst(self, obj):
        if len(obj.tekst) > 200:
            return f"{obj.tekst[:200]}..."
        return obj.tekst

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
