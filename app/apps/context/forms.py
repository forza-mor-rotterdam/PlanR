from apps.context.constanten import FILTER_KEYS, KOLOM_KEYS
from apps.context.models import Context
from apps.services.meldingen import MeldingenService
from apps.services.onderwerpen import render_onderwerp
from django import forms
from utils.forms import RadioSelect


class ContextAanpassenForm(forms.ModelForm):
    template = forms.ChoiceField(
        widget=RadioSelect(
            attrs={
                "class": "list--form-radio-input",
            }
        ),
        label="Sjabloon",
        required=True,
        choices=Context.TemplateOpties.choices,
    )
    filters = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "form-check-input",
            }
        ),
        label="Filters",
        required=False,
        choices=[(f, f) for f in FILTER_KEYS],
    )

    kolommen = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "form-check-input",
            }
        ),
        label="Kolommen",
        required=False,
        choices=[(f, f) for f in KOLOM_KEYS],
    )

    standaard_filters = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "form-check-input",
            }
        ),
        label="Onderwerpen",
        required=False,
        choices=(),
    )
    taaktypes = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "form-check-input",
            }
        ),
        label="Taaktypes",
        required=False,
        choices=(),
    )

    class Meta:
        model = Context
        fields = (
            "naam",
            "filters",
            "kolommen",
            "standaard_filters",
            "taaktypes",
            "template",
        )

    def __init__(self, *args, **kwargs):
        kwargs.get("instance")
        super().__init__(*args, **kwargs)
        onderwerp_alias_list = (
            MeldingenService().onderwerp_alias_list().get("results", [])
        )
        taakapplicaties = MeldingenService().taakapplicaties().get("results", [])
        taaktypes = [tt for ta in taakapplicaties for tt in ta.get("taaktypes", [])]
        self.fields["standaard_filters"].choices = [
            (
                onderwerp_alias.get("pk"),
                render_onderwerp(
                    onderwerp_alias.get("bron_url"), onderwerp_alias.get("pk")
                ),
            )
            for onderwerp_alias in onderwerp_alias_list
        ]
        self.fields["taaktypes"].choices = [
            (
                taaktype.get("_links", {}).get("self"),
                taaktype.get("omschrijving"),
            )
            for taaktype in taaktypes
        ]


class ContextAanmakenForm(ContextAanpassenForm):
    class Meta:
        model = Context
        fields = (
            "naam",
            "filters",
            "kolommen",
            "standaard_filters",
            "taaktypes",
            "template",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[
            "naam"
        ].help_text = "Omschrijf de rol zo concreet mogelijk, bijvoorbeeld ‘Teamleider Inzameling Noord’."
        self.fields[
            "filters"
        ].help_text = (
            "De hier geselecteerde opties worden getoond in het Filter-menu van PlanR."
        )
        self.fields[
            "kolommen"
        ].help_text = "De hier geselecteerde opties worden getoond in PlanR."
        self.fields[
            "standaard_filters"
        ].help_text = "De hier geselecteerde opties worden getoond in PlanR."
        self.fields[
            "template"
        ].help_text = "Ieder sjabloon toont andere informatie. Het ‘Standaard’ sjabloon voldoet voor de meeste afdelingen."
        self.fields["filters"].label = "Welke filters zijn relevant voor deze rol?"
