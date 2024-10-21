import logging

from apps.main.constanten import PDOK_WIJKEN
from apps.main.services import OnderwerpenService
from django import forms

logger = logging.getLogger(__name__)


class DashboardForm(forms.Form):
    invalidate_cache = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
        required=False,
        initial=False,
    )
    onderwerp = forms.ChoiceField(
        # widget=forms.CheckboxSelectMultiple(
        #     attrs={
        #         "class": "list--form-radio-input",
        #         "data-action": "change->bijlagen#updateImageDisplay",
        #     }
        # ),
        required=False,
    )
    wijk = forms.ChoiceField(
        # widget=forms.RadioSelect(
        #     attrs={
        #         "class": "list--form-radio-input",
        #         "data-action": "change->bijlagen#updateImageDisplay",
        #     }
        # ),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        onderwerpen_service = OnderwerpenService()
        onderwerpen = onderwerpen_service.get_onderwerpen()

        wijk_choices = [[c.get("wijknaam"), c.get("wijknaam")] for c in PDOK_WIJKEN]
        wijk_choices.insert(0, ["", "---"])
        onderwerp_choices = [[c.get("name"), c.get("name")] for c in onderwerpen]
        onderwerp_choices.insert(0, ["", "---"])

        self.fields["wijk"].choices = wijk_choices
        self.fields["onderwerp"].choices = onderwerp_choices
