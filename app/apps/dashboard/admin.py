from apps.dashboard.models import (
    Databron,
    DoorlooptijdenAfgehandeldeMeldingen,
    NieuweMeldingAantallen,
    NieuweSignaalAantallen,
    NieuweTaakopdrachten,
    StatusVeranderingDuurMeldingen,
    TaakopdrachtDoorlooptijden,
    TaaktypeAantallenPerMelding,
    Tijdsvak,
)
from apps.dashboard.tasks import tijdsvakdata_vernieuwen
from django import forms
from django.contrib import admin
from django.contrib.admin import DateFieldListFilter


@admin.action(description="Tijdsvak data vernieuwen")
def action_tijdsvak_data_vernieuwen(modeladmin, request, queryset):
    for tijdsvak in queryset.all():
        tijdsvakdata_vernieuwen.delay(tijdsvak.id)


class TijdsvakExtendsForm(forms.ModelForm):
    class Meta:
        model = DoorlooptijdenAfgehandeldeMeldingen
        exclude = ["databron"]


class DatabronAdmin(admin.ModelAdmin):
    list_display = ("brontype", "url", "start_datumtijd_param", "eind_datumtijd_param")
    list_editable = (
        "url",
        "start_datumtijd_param",
        "eind_datumtijd_param",
    )


class TijdsvakExtendsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "start_datumtijd",
        "eind_datumtijd",
        "databron",
        "periode",
        "valide_data",
    )
    form = TijdsvakExtendsForm
    actions = (action_tijdsvak_data_vernieuwen,)
    list_filter = (
        ("start_datumtijd", DateFieldListFilter),
        ("eind_datumtijd", DateFieldListFilter),
        "periode",
    )


class TijdsvakAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "start_datumtijd",
        "eind_datumtijd",
        "databron",
        "periode",
        "valide_data",
    )
    actions = (action_tijdsvak_data_vernieuwen,)
    list_filter = (
        ("start_datumtijd", DateFieldListFilter),
        ("eind_datumtijd", DateFieldListFilter),
        "databron",
        "periode",
    )


admin.site.register(Databron, DatabronAdmin)
admin.site.register(DoorlooptijdenAfgehandeldeMeldingen, TijdsvakExtendsAdmin)
admin.site.register(StatusVeranderingDuurMeldingen, TijdsvakExtendsAdmin)
admin.site.register(NieuweMeldingAantallen, TijdsvakExtendsAdmin)
admin.site.register(NieuweSignaalAantallen, TijdsvakExtendsAdmin)
admin.site.register(NieuweTaakopdrachten, TijdsvakExtendsAdmin)
admin.site.register(TaaktypeAantallenPerMelding, TijdsvakExtendsAdmin)
admin.site.register(TaakopdrachtDoorlooptijden, TijdsvakExtendsAdmin)
admin.site.register(Tijdsvak, TijdsvakAdmin)
