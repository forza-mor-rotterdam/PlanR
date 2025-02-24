import logging

from apps.main.models import StandaardExterneOmschrijving
from django import forms

logger = logging.getLogger(__name__)


class StandaardExterneOmschrijvingAanpassenForm(forms.ModelForm):
    titel = forms.CharField(
        label="Afhandelreden",
        help_text="Deze tekst wordt gebruikt om de juiste standaard tekst te selecteren.",
        widget=forms.TextInput(
            attrs={
                "data-externeomschrijvingformulier-target": "externeOmschrijvingTitel",
                "name": "titel",
            }
        ),
    )
    tekst = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 10,
                "cols": 38,
                "style": "resize: none;",
                "data-externeomschrijvingformulier-target": "externeOmschrijvingTekst",
                "data-action": "externeomschrijvingformulier#onChangeExterneOmschrijvingTekst",
                "name": "tekst",
            }
        ),
        label="Bericht naar melder",
        max_length=1000,
    )

    class Meta:
        model = StandaardExterneOmschrijving
        fields = ["titel", "tekst"]


class StandaardExterneOmschrijvingAanmakenForm(
    StandaardExterneOmschrijvingAanpassenForm
):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields[
        #     "titel"
        # ].help_text = "Geef een titel op voor de standaard tekst."
        # self.fields[
        #     "tekst"
        # ].help_text = "Geef een standaard tekst op van maximaal 2000 tekens. Deze tekst kan bij het afhandelen van een melding aangepast worden."


class StandaardExterneOmschrijvingSearchForm(forms.Form):
    search = forms.CharField(
        label="Zoeken",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Zoek standaard tekst"}),
    )
