from urllib.parse import urlparse

from apps.context.constanten import FILTERS, KOLOMMEN
from apps.context.models import Context
from django import forms


class CheckboxSelectMultiplePaths(forms.CheckboxSelectMultiple):
    def optgroups(self, name, value, attrs=None):
        """Return a list of optgroups for this widget."""
        groups = []
        has_selected = False

        for index, (option_value, option_label) in enumerate(self.choices):
            if option_value is None:
                option_value = ""

            subgroup = []
            if isinstance(option_label, (list, tuple)):
                group_name = option_value
                subindex = 0
                choices = option_label
            else:
                group_name = None
                subindex = None
                choices = [(option_value, option_label)]
            groups.append((group_name, subgroup, index))

            for subvalue, sublabel in choices:
                selected = urlparse(str(subvalue)).path in [
                    urlparse(v).path for v in value
                ] and (not has_selected or self.allow_multiple_selected)
                has_selected |= selected
                subgroup.append(
                    self.create_option(
                        name,
                        subvalue,
                        sublabel,
                        selected,
                        index,
                        subindex=subindex,
                        attrs=attrs,
                    )
                )
                if subindex is not None:
                    subindex += 1
        return groups


class ContextAanpassenForm(forms.ModelForm):
    template = forms.ChoiceField(
        widget=forms.RadioSelect(
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
        choices=[(f.key(), f.label()) for f in FILTERS],
    )

    kolommen = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "form-check-input",
            }
        ),
        label="Kolommen",
        required=False,
        choices=[(f.key(), f.th_label(f)) for f in KOLOMMEN],
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
        widget=CheckboxSelectMultiplePaths(
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
        self.taaktypes = kwargs.pop("taaktypes", [])
        self.onderwerp_alias_list = kwargs.pop("onderwerp_alias_list", [])
        self.onderwerpen_service = kwargs.pop("onderwerpen_service", None)
        super().__init__(*args, **kwargs)

        # Group onderwerpen by group_uuid
        onderwerpen_grouped = {}
        for onderwerp_alias in self.onderwerp_alias_list:
            onderwerp = self.onderwerpen_service.get_onderwerp(
                onderwerp_alias.get("bron_url"),
                force_cache=True,
            )
            group_uuid = onderwerp.get("group_uuid")
            group_name = self.onderwerpen_service.get_groep(
                group_uuid,
                force_cache=True,
            ).get("name")
            if group_uuid not in onderwerpen_grouped:
                onderwerpen_grouped[group_uuid] = {"name": group_name, "items": []}
            onderwerpen_grouped[group_uuid]["items"].append(
                (onderwerp_alias.get("pk"), onderwerp.get("name", "Niet gevonden!"))
            )

        # Different way to get the groups using OnderwerpenService().get_onderwerpen()
        # onderwerpen_grouped = {}
        # onderwerpen = OnderwerpenService().get_onderwerpen()
        # for onderwerp in onderwerpen:
        #     group_uuid = onderwerp.get("group_uuid")
        #     group_name = (
        #         OnderwerpenService().get_groep(onderwerp.get("group_uuid")).get("name")
        #     )
        #     onderwerpen_grouped.setdefault(
        #         group_uuid, {"name": group_name, "items": []}
        #     )
        #     onderwerpen_grouped[group_uuid]["items"].append(
        #         (
        #             onderwerp.get("pk"),
        #             onderwerp.get("name", "Niet gevonden!"),
        #         )
        #     )

        # Format onderwerpen choices
        self.onderwerpen_choices = []
        for group_uuid, group_data in onderwerpen_grouped.items():
            group_name = group_data["name"]
            group_items = sorted(group_data["items"], key=lambda x: x[1])
            self.onderwerpen_choices.append(
                (group_name, [(pk, label) for pk, label in group_items])
            )

        # Assign choices to standaard_filters field
        self.fields["standaard_filters"].choices = self.onderwerpen_choices
        self.fields["taaktypes"].choices = [
            (
                taaktype.get("_links", {}).get("taakapplicatie_taaktype_url"),
                taaktype.get("omschrijving"),
            )
            for taaktype in self.taaktypes
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
