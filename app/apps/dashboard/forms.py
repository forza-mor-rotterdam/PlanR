import logging

from apps.main.constanten import PDOK_WIJKEN
from apps.main.services import OnderwerpenService
from django import forms
from django.template.loader import get_template

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


class RadioSelectCompactChoiceField(forms.ChoiceField):
    icon = None

    class RadioSelect(forms.RadioSelect):
        template_name = "widgets/field_radio_select_compact.html"
        option_template_name = "widgets/field_radio_select_compact_option.html"

    widget = RadioSelect

    @property
    def template_name(self):
        return "forms/field_radio_select_compact.html"

    @template_name.setter
    def template_name(self, value):
        self._template_name = value

    def widget_attrs(self, widget):
        widget_action = "radio-select-compact#onChangeHandler"
        icon_template = ""
        try:
            icon_template = get_template(widget.attrs.get("icon")).render()
        except Exception:
            ...

        self.icon = icon_template
        data_actions = [
            action.strip() for action in widget.attrs.get("data-action").split()
        ]
        if widget_action not in data_actions:
            data_actions.append(widget_action)

        attrs = super().widget_attrs(widget)
        attrs.update(
            {
                "class": "list--form-radio-input",
                "data-action": " ".join(data_actions),
                "wrap_label": False,
            }
        )
        return attrs


class DashboardV2Form(forms.Form):
    weergave = RadioSelectCompactChoiceField(
        widget=RadioSelectCompactChoiceField.widget(
            attrs={
                "data-action": "dashboard#onWeergaveChangeHandler",
                "icon": "icons/house.svg",
            }
        ),
        choices=(
            ("wijk", "Wijk"),
            ("buurt", "Buurt"),
        ),
        initial="wijk",
    )
    stadsdeel = RadioSelectCompactChoiceField(
        widget=RadioSelectCompactChoiceField.widget(
            attrs={
                "data-action": "dashboard#onStadsdeelChangeHandler",
                "icon": "icons/city.svg",
            },
        ),
        choices=(
            ("", "Heel Rotterdam"),
            ("noord", "Rotterdam noord"),
            ("zuid", "Rotterdam zuid"),
        ),
        initial="",
        required=False,
    )
    periode = RadioSelectCompactChoiceField(
        widget=RadioSelectCompactChoiceField.widget(
            attrs={
                "data-action": "dashboard#onPeriodeChangeHandler",
                "icon": "icons/calendar.svg",
            }
        ),
        choices=(
            ("1", "1 uur"),
            ("24", "Één dag"),
            ("48", "2 dagen"),
            ("168", "Één week"),
            ("672", "Één maand"),
        ),
        initial="1",
    )
