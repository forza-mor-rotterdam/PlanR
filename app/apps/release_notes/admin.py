from apps.main.utils import truncate_tekst
from apps.release_notes.tasks import task_aanmaken_afbeelding_versies
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import Bijlage, ReleaseNote

# from django_ckeditor_5.widgets import CKEditor5Widget


class BijlageInline(GenericTabularInline):
    model = Bijlage
    extra = 1


class ReleaseNoteAdmin(admin.ModelAdmin):
    def korte_tekst(self, obj):
        return truncate_tekst(obj.beschrijving)

    # formfield_overrides = {
    #     models.TextField: {"widget": CKEditor5Widget()},
    # }
    list_display = (
        "titel",
        "bericht_type",
        "korte_tekst",
        "aangemaakt_op",
        "publicatie_datum",
    )
    search_fields = ("titel",)
    list_filter = ("aangemaakt_op", "publicatie_datum", "bericht_type")
    ordering = ["-aangemaakt_op"]
    inlines = [BijlageInline]

    # form = ReleaseNoteAanpassenForm
    korte_tekst.short_description = "Beschrijving"

    class Meta:
        model = ReleaseNote
        fields = "__all__"


@admin.action(description="Maak afbeelding versies voor selectie")
def action_aanmaken_afbeelding_versies(modeladmin, request, queryset):
    for bijlage in queryset.all():
        task_aanmaken_afbeelding_versies.delay(bijlage.id)


class BijlageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "aangemaakt_op",
        "bestand",
        "is_afbeelding",
        "mimetype",
        "content_object",
        "afbeelding",
    )
    actions = (action_aanmaken_afbeelding_versies,)


admin.site.register(Bijlage, BijlageAdmin)
admin.site.register(ReleaseNote, ReleaseNoteAdmin)
