import logging

from apps.main.models import (
    SPECIFICATIE_CACHE_TIMEOUT,
    STATUS_NIET_OPGELOST,
    STATUS_NIET_OPGELOST_REDENEN_CHOICES,
    STATUS_NIET_OPGELOST_REDENEN_TITEL,
    ZICHTBAARHEID_CHOICES,
    MeldingAfhandelreden,
    StandaardExterneOmschrijving,
)
from apps.main.services import MORCoreService
from django import forms
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class MeldingAfhandelredenRadioSelect(forms.RadioSelect):
    def __init__(self, *args, **kwargs):
        self.extra_data = kwargs.pop("extra_data", [])
        super().__init__(*args, **kwargs)

    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        attrs["disabled"] = self.extra_data.get(value, 0)
        return super().create_option(
            name, value, label, selected, index, subindex=subindex, attrs=attrs
        )


class StandaardExterneOmschrijvingForm(forms.ModelForm):
    titel = forms.CharField(
        label="Titel van de tekst",
        help_text="Deze titel wordt gebruikt om de juiste standaard tekst te selecteren.",
        widget=forms.TextInput(
            attrs={
                "data-externeomschrijvingformulier-target": "externeOmschrijvingTitel",
                "data-action": "externeomschrijvingformulier#onChangeHandler",
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
                "data-action": "externeomschrijvingformulier#onChangeHandler",
                "name": "tekst",
            }
        ),
        label="Bericht naar melder",
        max_length=1000,
    )
    zichtbaarheid = forms.ChoiceField(
        widget=forms.RadioSelect(
            attrs={
                "class": "list--form-radio-input",
                "data-externeomschrijvingformulier-target": "zichtbaarheidField",
                "data-action": "externeomschrijvingformulier#onChangeHandler",
            }
        ),
        choices=ZICHTBAARHEID_CHOICES,
    )
    reden = forms.ModelChoiceField(
        queryset=MeldingAfhandelreden.objects.all(),
        widget=forms.RadioSelect(
            attrs={
                "class": "list--form-radio-input",
                "data-externeomschrijvingformulier-target": "nietOpgelostRedenField",
                "data-action": "externeomschrijvingformulier#onChangeHandler",
            }
        ),
        required=False,
    )
    specificatie_opties = forms.ChoiceField(
        widget=forms.RadioSelect(
            attrs={
                "class": "list--form-radio-input",
                # "class": "form-check-input",
                "data-action": "externeomschrijvingformulier#onChangeHandler",
                "data-externeomschrijvingformulier-target": "nietOpgelostSpecificatieOptiesField",
            }
        ),
        required=False,
    )

    def clean_specificatie_opties(self):
        data = self.cleaned_data["specificatie_opties"]
        if data:
            return [data]
        return []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        specificatie_lijst = (
            MORCoreService()
            .specificatie_lijst(
                params={
                    "limit": 100,
                    "is_verwijderd": False,
                },
                force_cache=True,
                cache_timeout=SPECIFICATIE_CACHE_TIMEOUT,
            )
            .get("results", [])
        )
        self.fields["zichtbaarheid"].choices = [
            (zichtbaarheid[0], zichtbaarheid[1])
            for zichtbaarheid in ZICHTBAARHEID_CHOICES
            if len(self.fields["reden"].choices)
            or (
                not len(self.fields["reden"].choices)
                and zichtbaarheid[0] != STATUS_NIET_OPGELOST
            )
        ]
        self.fields["specificatie_opties"].choices = [
            (
                specificatie.get("_links", {}).get("self", {}).get("href", "-"),
                specificatie.get("naam", "-"),
            )
            for specificatie in specificatie_lijst
        ]

    class Meta:
        model = StandaardExterneOmschrijving
        fields = [
            "titel",
            "tekst",
            "zichtbaarheid",
            "reden",
            "specificatie_opties",
        ]


class MeldingAfhandelredenForm(forms.ModelForm):
    reden = forms.ChoiceField(
        widget=MeldingAfhandelredenRadioSelect(
            attrs={
                "class": "list--form-radio-input",
                "data-beheer--melding-afhandelreden-target": "reden",
            }
        ),
        required=False,
        choices=STATUS_NIET_OPGELOST_REDENEN_CHOICES,
    )
    toelichting = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 5,
                "cols": 38,
                "style": "resize: none;",
            }
        ),
        required=False,
        max_length=250,
    )
    specificatie_opties = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "form-check-input",
                "classList": "list--form-check-input list--form-check-input--full-width",
                "data-beheer--melding-afhandelreden-target": "specificatieOpties",
            }
        ),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        specificatie_lijst = (
            MORCoreService()
            .specificatie_lijst(
                params={
                    "limit": 100,
                    "is_verwijderd": False,
                },
                force_cache=True,
                cache_timeout=SPECIFICATIE_CACHE_TIMEOUT,
            )
            .get("results", [])
        )

        melding_afhandelredenen = MeldingAfhandelreden.objects.all()
        if self.instance.id:
            melding_afhandelredenen = melding_afhandelredenen.exclude(
                id=self.instance.id,
            )
        gebruikte_specificatie_urls = list(
            set(
                [
                    url
                    for url_list in melding_afhandelredenen.filter(
                        specificatie_opties__isnull=False
                    ).values_list("specificatie_opties", flat=True)
                    for url in url_list
                ]
            )
        )
        gebruikte_redenen = list(
            melding_afhandelredenen.values_list("reden", flat=True)
        )
        specificatie_opties = [
            (
                specificatie.get("_links", {}).get("self", {}).get("href", "-"),
                specificatie.get("naam", "-"),
            )
            for specificatie in specificatie_lijst
        ]
        specificatie_choices = [
            (specificatie[0], specificatie[1])
            for specificatie in specificatie_opties
            if specificatie[0] not in gebruikte_specificatie_urls
        ]
        if len(specificatie_choices) == 0:
            self.fields["specificatie_opties"].widget = forms.HiddenInput()
            self.fields["specificatie_opties"].choices = []
        else:
            self.fields["specificatie_opties"].choices = specificatie_choices

        reden_choices = [
            (
                choice[0],
                STATUS_NIET_OPGELOST_REDENEN_TITEL.get(choice[0], choice[0]),
                choice[0] not in gebruikte_redenen,
            )
            for choice in STATUS_NIET_OPGELOST_REDENEN_CHOICES
        ]
        reden_extra_data = {choice[0]: not choice[2] for choice in reden_choices}
        reden_choices = [(choice[0], choice[1]) for choice in reden_choices]

        self.fields["reden"] = forms.ChoiceField(
            widget=MeldingAfhandelredenRadioSelect(
                attrs={
                    "class": "list--form-radio-input",
                    "data-beheer--melding-afhandelreden-target": "reden",
                },
                extra_data=reden_extra_data,
            ),
            required=False,
            choices=reden_choices,
        )

    class Meta:
        model = MeldingAfhandelreden
        fields = [
            "reden",
            "toelichting",
            "specificatie_opties",
        ]


class StandaardExterneOmschrijvingSearchForm(forms.Form):
    search = forms.CharField(
        label="Zoeken",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Zoek standaard tekst"}),
    )


class SpecificatieForm(forms.Form):
    naam = forms.CharField(
        label="Naam",
        required=True,
    )

    def clean_naam(self):
        data = self.cleaned_data["naam"]
        zoek_resultaten = (
            MORCoreService()
            .specificatie_lijst(
                params={
                    "naam": data,
                    "limit": 1,
                },
                force_cache=True,
                cache_timeout=SPECIFICATIE_CACHE_TIMEOUT,
            )
            .get("results", [])
        )
        if zoek_resultaten:
            raise ValidationError(
                f"Deze naam bestaat al{', maar is verwijderd' if zoek_resultaten[0].get('verwijderd_op') else ''}"
            )
        return data
