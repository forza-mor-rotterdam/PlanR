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

    begraafplaats = forms.MultipleChoiceField(
        label="Locatie",
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "list--form-check-input",
                "hideLabel": True,
            }
        ),
        choices=[],
        required=False,
    )

    status = forms.MultipleChoiceField(
        label="Status",
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "list--form-check-input",
                "hideLabel": True,
            }
        ),
        choices=[],
        required=False,
    )

    onderwerp = forms.MultipleChoiceField(
        label="Categorie",
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "list--form-check-input",
                "hideLabel": True,
            }
        ),
        choices=[],
        required=False,
    )

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

    def __init__(self, *args, **kwargs):
        offset_options = kwargs.pop("offset_options", None)
        locatie_opties = kwargs.pop("locatie_opties", None)
        status_opties = kwargs.pop("status_opties", None)
        onderwerp_opties = kwargs.pop("onderwerp_opties", None)
        super().__init__(*args, **kwargs)
        self.fields["offset"].choices = offset_options
        self.fields["begraafplaats"].choices = locatie_opties
        self.fields["status"].choices = status_opties
        self.fields["onderwerp"].choices = onderwerp_opties


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
