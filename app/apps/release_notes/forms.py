import logging

from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from django_ckeditor_5.widgets import CKEditor5Widget

from .models import Bijlage, ReleaseNote

logger = logging.getLogger(__name__)

BijlageFormSet = generic_inlineformset_factory(
    Bijlage,
    fields=["bestand"],
    extra=0,
    can_delete=True,
)


class ReleaseNoteAanpassenForm(forms.ModelForm):
    bericht_type = forms.ChoiceField(
        widget=forms.RadioSelect(
            attrs={
                "data-action": "change->berichten-beheer#berichtTypeChangeHandler",
            }
        ),
        choices=ReleaseNote.BerichtTypeOpties.choices,
        initial=ReleaseNote.BerichtTypeOpties.RELEASE_NOTE,
    )
    titel = forms.CharField(
        label="Titel",
        widget=forms.TextInput(),
    )
    korte_beschrijving = forms.CharField(
        label="Korte beschrijving",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "data-controller": "characterCount",
                "data-action": "characterCount#onChangeText",
            }
        ),
        max_length=600,
    )
    beschrijving = forms.CharField(
        widget=CKEditor5Widget(
            attrs={
                "name": "beschrijving",
            }
        ),
        label="Beschrijving",
        required=False,
        help_text="Max 5000 tekens.",
        max_length=5000,
    )

    link_titel = forms.CharField(
        label="Link titel",
        widget=forms.TextInput(
            attrs={
                "data-controller": "characterCount",
                "data-action": "characterCount#onChangeText",
            }
        ),
        required=False,
        max_length=20,
    )

    toast_miliseconden_zichtbaar = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False,
        initial=6000,
    )

    publicatie_datum = forms.DateTimeField(
        label="Publicatie datum",
        required=True,
        help_text="Release notes worden vanaf de publicatie datum 5 weken lang getoond.",
    )

    bijlagen = forms.FileField(
        label="Afbeelding of GIF",
        required=False,
        widget=forms.widgets.FileInput(
            attrs={
                "accept": ".jpg, .jpeg, .png, .heic, .gif",
                "data-action": "change->bijlagen#updateImageDisplay",
                "data-bijlagen-target": "bijlagenExtra",
                # "multiple": "multiple",
                "hideLabel": True,
            }
        ),
    )

    formset = BijlageFormSet(queryset=Bijlage.objects.none(), prefix="bijlage")

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("notificatie_niveau") in (
            ReleaseNote.NotificatieNiveauOpties.ERROR,
            ReleaseNote.NotificatieNiveauOpties.WARNING,
        ):
            cleaned_data["toast_miliseconden_zichtbaar"] = 10000
        return cleaned_data

    class Meta:
        model = ReleaseNote
        fields = [
            "bericht_type",
            "notificatie_niveau",
            "titel",
            "korte_beschrijving",
            "link_titel",
            "link_url",
            "beschrijving",
            "publicatie_datum",
            "einde_publicatie_datum",
            "toast_miliseconden_zichtbaar",
        ]


class ReleaseNoteAanmakenForm(ReleaseNoteAanpassenForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields[
        #     "titel"
        # ].help_text = "Geef een titel op voor de standaard tekst."
        # self.fields[
        #     "tekst"
        # ].help_text = "Geef een standaard tekst op van maximaal 2000 tekens. Deze tekst kan bij het afhandelen van een melding aangepast worden."


class ReleaseNoteSearchForm(forms.Form):
    search = forms.CharField(
        label="Zoeken",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Zoek release note"}),
    )
