import logging

from django import forms

logger = logging.getLogger(__name__)


class DashboardForm(forms.Form):
    onderwerp = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "list--form-radio-input",
                "data-action": "change->bijlagen#updateImageDisplay",
            }
        ),
        required=False,
    )
    wijk = forms.ChoiceField(
        widget=forms.RadioSelect(
            attrs={
                "class": "list--form-radio-input",
                "data-action": "change->bijlagen#updateImageDisplay",
            }
        ),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        wijken = kwargs.pop("wijken", [])
        onderwerpen = kwargs.pop("onderwerpen", [])
        super().__init__(*args, **kwargs)

        self.fields["wijk"].choices = [[c, c] for c in wijken]
        self.fields["onderwerp"].choices = [[c, c] for c in onderwerpen]
