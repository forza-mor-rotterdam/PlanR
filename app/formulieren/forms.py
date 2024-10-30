from django import forms
from formulieren.fields import CharField, MultipleChoiceField
from formulieren.widgets import CheckBoxSelectMultiple


class BasisForm(forms.Form):
    basis_input = CharField()
    basis_multiple_select_checkbox = MultipleChoiceField(
        widget=CheckBoxSelectMultiple(),
        choices=(
            ("a", "A"),
            ("b", "B"),
            ("c", "C"),
        ),
    )
