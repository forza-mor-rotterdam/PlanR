from apps.context.constanten import FILTER_NAMEN, KOLOM_NAMEN
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
        choices=[(f, f) for f in FILTER_NAMEN],
    )

    kolommen = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "form-check-input",
            }
        ),
        label="Kolommen",
        required=False,
        choices=[(f, f) for f in KOLOM_NAMEN],
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

    class Meta:
        model = Context
        fields = ("naam", "filters", "kolommen", "standaard_filters", "template")

    def __init__(self, *args, **kwargs):
        kwargs.get("instance")
        super().__init__(*args, **kwargs)
        onderwerp_alias_list = (
            MeldingenService().onderwerp_alias_list().get("results", [])
        )
        self.fields["standaard_filters"].choices = [
            (
                onderwerp_alias.get("pk"),
                render_onderwerp(
                    onderwerp_alias.get("bron_url"), onderwerp_alias.get("pk")
                ),
            )
            for onderwerp_alias in onderwerp_alias_list
        ]


class ContextAanmakenForm(ContextAanpassenForm):
    class Meta:
        model = Context
        fields = (
            "naam",
            "filters",
            "kolommen",
            "standaard_filters",
            "template",
        )
