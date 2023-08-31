from django import forms

BEHANDEL_OPTIES = (
    (
        "ja",
        "Ja",
        "We zijn met uw melding aan de slag gegaan en hebben het probleem opgelost.",
        "afgehandeld",
        "opgelost",
    ),
    (
        "nee",
        "Nee",
        "We zijn met uw melding aan de slag gegaan maar deze kan niet direct worden opgelost. Want...",
        "afgehandeld",
        None,
    ),
)
TAAK_BEHANDEL_OPTIES = (
    (
        "ja",
        "Ja",
        "We zijn met uw melding aan de slag gegaan en hebben het probleem opgelost.",
        "voltooid",
        "opgelost",
    ),
    (
        "nee",
        "Nee, het probleem kan niet worden opgelost.",
        "We zijn met uw melding aan de slag gegaan, maar konden het probleem helaas niet oplossen. Want...",
        "voltooid",
        None,
    ),
)

TAAK_BEHANDEL_STATUS = {bo[0]: bo[3] for bo in TAAK_BEHANDEL_OPTIES}
TAAK_BEHANDEL_RESOLUTIE = {bo[0]: bo[4] for bo in TAAK_BEHANDEL_OPTIES}
BEHANDEL_STATUS = {bo[0]: bo[3] for bo in BEHANDEL_OPTIES}
BEHANDEL_RESOLUTIE = {bo[0]: bo[4] for bo in BEHANDEL_OPTIES}


class CheckboxSelectMultipleThumb(forms.CheckboxSelectMultiple):
    ...


class FilterForm(forms.Form):
    filter_velden = []
    ordering = forms.CharField(
        widget=forms.HiddenInput(),
        initial="aangemaakt_op",
        required=False,
    )

    offset = forms.ChoiceField(
        widget=forms.RadioSelect(
            attrs={
                "class": "list--form-check-input",
                "hideLabel": True,
            }
        ),
        required=False,
    )

    limit = forms.CharField(
        widget=forms.HiddenInput,
        initial="10",
        required=False,
    )

    def filters(self):
        for field_name in self.fields:
            if field_name in self.filter_velden:
                yield self[field_name]

    def __init__(self, *args, **kwargs):
        velden = kwargs.pop("filter_velden", None)
        self.filter_velden = [v.get("naam") for v in velden]
        offset_options = kwargs.pop("offset_options", None)
        super().__init__(*args, **kwargs)
        self.fields["offset"].choices = offset_options
        for v in velden:
            self.fields[v.get("naam")] = forms.MultipleChoiceField(
                label=f"{v.get('naam')} ({v.get('aantal_actief')}/{len(v.get('opties', []))})",
                widget=forms.CheckboxSelectMultiple(
                    attrs={
                        "class": "list--form-check-input",
                        "hideLabel": True,
                    }
                ),
                choices=v.get("opties", []),
                required=False,
            )


class LoginForm(forms.Form):
    username = forms.CharField(label="Personeelsnummer", widget=forms.TextInput())
    password = forms.CharField(label="Wachtwoord", widget=forms.PasswordInput())


class RadioSelect(forms.RadioSelect):
    option_template_name = "widgets/radio_option.html"


class InformatieToevoegenForm(forms.Form):
    opmerking = forms.CharField(
        label="Voeg een opmerking toe",
        widget=forms.Textarea(
            attrs={"class": "form-control", "data-testid": "information", "rows": "4"}
        ),
        required=False,
    )

    bijlagen_extra = forms.FileField(
        widget=forms.widgets.FileInput(
            attrs={
                "accept": ".jpg, .jpeg, .png, .heic",
                "data-action": "change->bijlagen#updateImageDisplay",
                "data-bijlagen-target": "bijlagenExtra",
            }
        ),
        label="Voeg één of meerdere foto's toe",
        required=False,
    )


class TaakStartenForm(forms.Form):
    taaktype = forms.ChoiceField(
        widget=forms.Select(),
        label="Taak",
        choices=(
            ("graf_ophogen", "Graf ophogen"),
            ("steen_rechtzetten", "Steen rechtzetten"),
            ("snoeien", "Snoeien"),
        ),
        required=True,
    )

    bericht = forms.CharField(
        label="Interne opmerking",
        help_text="Deze tekst wordt niet naar de melder verstuurd.",
        widget=forms.Textarea(
            attrs={"class": "form-control", "data-testid": "information", "rows": "4"}
        ),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        taaktypes = kwargs.pop("taaktypes", None)
        super().__init__(*args, **kwargs)
        self.fields["taaktype"].choices = taaktypes


class TaakAfrondenForm(forms.Form):
    status = forms.ChoiceField(
        widget=RadioSelect(
            attrs={
                "class": "list--form-radio-input",
            }
        ),
        label="Is het probleem opgelost?",
        choices=[[x[0], x[1]] for x in TAAK_BEHANDEL_OPTIES],
        required=True,
    )

    bijlagen = forms.FileField(
        widget=forms.widgets.FileInput(
            attrs={
                "accept": ".jpg, .jpeg, .png, .heic",
                "data-action": "change->bijlagen#updateImageDisplay",
                "data-bijlagen-target": "bijlagenAfronden",
            }
        ),
        label="Foto's",
        required=False,
    )

    omschrijving_intern = forms.CharField(
        label="Interne opmerking",
        help_text="Je kunt deze tekst aanpassen of eigen tekst toevoegen.",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "data-testid": "information",
                "rows": "4",
                "data-meldingbehandelformulier-target": "internalText",
            }
        ),
        required=False,
    )


class MeldingAfhandelenForm(forms.Form):

    omschrijving_extern = forms.CharField(
        label="Bericht voor de melder",
        help_text="Je kunt deze tekst aanpassen of eigen tekst toevoegen.",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "data-testid": "message",
                "rows": "4",
                "data-meldingbehandelformulier-target": "externalText",
            }
        ),
        required=True,
    )

    omschrijving_intern = forms.CharField(
        label="Interne opmerking",
        help_text="Deze tekst wordt niet naar de melder verstuurd.",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": "4",
                "data-meldingbehandelformulier-target": "internalText",
            }
        ),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        # bijlagen = kwargs.pop("bijlagen", None)
        super().__init__(*args, **kwargs)
        # print("FORMS bijlagen = = = >")
        # print(bijlagen)
        # self.fields["bijlagen"].choices = bijlagen
        # self.fields["bijlagen"].choices = [
        #     (str(m.get("afbeelding")), m.get("afbeelding")) for m in bijlagen
        # ]

    # def terugsturen(self, data):
    #     if data.get("afhandel_reden") == ""
