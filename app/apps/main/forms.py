import base64
import json
import logging

from apps.context.constanten import KOLOMMEN, KOLOMMEN_KEYS
from apps.main.models import StandaardExterneOmschrijving
from django import forms
from django.core.files.storage import default_storage
from django.utils import timezone
from utils.rd_convert import rd_to_wgs

logger = logging.getLogger(__name__)


def is_valid_callable(key):
    return key is not None and callable(key)


class CheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def create_option(self, *args, **kwargs):
        args = list(args)
        option_data = args[2]
        args[2] = args[2].get("label")
        option = super().create_option(*args, **kwargs)
        option["attrs"].update({"item_count": option_data.get("item_count")})
        option["attrs"].update({"selected": args[3]})
        return option


class MultipleChoiceField(forms.MultipleChoiceField):
    ...


TAAK_STATUS_VOLTOOID = "voltooid"
TAAK_RESOLUTIE_OPGELOST = "opgelost"
TAAK_RESOLUTIE_NIET_OPGELOST = "niet_opgelost"
TAAK_RESOLUTIE_GEANNULEERD = "geannuleerd"

TAAK_BEHANDEL_OPTIES = (
    (
        "ja",
        "Ja",
        "We zijn met uw melding aan de slag gegaan en hebben het probleem opgelost.",
        TAAK_STATUS_VOLTOOID,
        TAAK_RESOLUTIE_OPGELOST,
    ),
    (
        "nee",
        "Nee, het probleem kan niet worden opgelost.",
        "We zijn met uw melding aan de slag gegaan, maar konden het probleem helaas niet oplossen. Want...",
        TAAK_STATUS_VOLTOOID,
        TAAK_RESOLUTIE_NIET_OPGELOST,
    ),
)


class CheckboxSelectMultipleThumb(forms.CheckboxSelectMultiple):
    ...


class KolommenRadioSelect(forms.RadioSelect):
    template_name = "widgets/kolommen_multiple_input.html"


class FilterForm(forms.Form):
    filter_velden = []

    q = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "list--form-text-input",
                "hideLabel": True,
                "typeOfInput": "search",
                "placeHolder": "MeldR nummer",
            }
        ),
        label="Zoeken",
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
        initial="0",
        required=False,
    )

    limit = forms.CharField(
        widget=forms.HiddenInput,
        initial="10",
        required=False,
    )

    def geselecteerde_filters(self):
        return [
            {f.name: [label for value, label in f.field.choices if value in f.value()]}
            for f in self.filters()
        ]

    def filters(self):
        for field_name in self.fields:
            if field_name in self.filter_velden:
                yield self[field_name]

    def __init__(self, *args, **kwargs):
        velden = kwargs.pop("filter_velden", None)
        gebruiker_context = kwargs.pop("gebruiker_context", None)
        self.filter_velden = [v.get("naam") for v in velden]

        kolommen = KOLOMMEN
        if gebruiker_context:
            kolommen = [
                k
                for k in gebruiker_context.kolommen.get("sorted", [])
                if is_valid_callable(KOLOMMEN_KEYS.get(k))
            ]

        self.kolommen = [
            {
                "instance": KOLOMMEN_KEYS.get(k)({})
                if is_valid_callable(KOLOMMEN_KEYS.get(k))
                else None,
                "opties": [
                    KOLOMMEN_KEYS.get(k)({"ordering": "up"})
                    if is_valid_callable(KOLOMMEN_KEYS.get(k))
                    else None,
                    KOLOMMEN_KEYS.get(k)({"ordering": "down"})
                    if is_valid_callable(KOLOMMEN_KEYS.get(k))
                    else None,
                ],
            }
            for k in kolommen
        ]

        offset_options = kwargs.pop("offset_options", None)
        super().__init__(*args, **kwargs)

        choices = [
            (
                k.get("instance"),
                [
                    (o.ordering(), o) if is_valid_callable(o) else (None, None)
                    for o in k.get("opties", [])
                ],
            )
            for k in self.kolommen
        ]

        self.fields["ordering"] = forms.ChoiceField(
            label="Ordering",
            widget=KolommenRadioSelect(attrs={}),
            choices=choices,
            required=False,
        )

        self.fields["offset"].choices = (
            offset_options if offset_options else [("0", "0")]
        )

        for v in velden:
            self.fields[v.get("naam")] = MultipleChoiceField(
                label=f"{v.get('naam')} ({v.get('aantal_actief')}/{len(v.get('opties', []))})",
                widget=CheckboxSelectMultiple(
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
            attrs={
                "class": "form-control",
                "data-testid": "information",
                "rows": "4",
            }
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
            attrs={
                "class": "form-control",
                "data-testid": "information",
                "rows": "4",
            }
        ),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        taaktypes = kwargs.pop("taaktypes", None)
        super().__init__(*args, **kwargs)
        self.fields["taaktype"].choices = taaktypes


class TaakAfrondenForm(forms.Form):
    resolutie = forms.ChoiceField(
        widget=RadioSelect(
            attrs={
                "class": "list--form-radio-input",
                "data-action": "change->bijlagen#updateImageDisplay",
            }
        ),
        label="Is de taak afgehandeld?",
        choices=[[x[4], x[1]] for x in TAAK_BEHANDEL_OPTIES],
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

    def __init__(self, *args, **kwargs):
        taakopdracht_opties = kwargs.pop("taakopdracht_opties", None)
        super().__init__(*args, **kwargs)

        if taakopdracht_opties:
            self.fields["taakopdracht"] = forms.ChoiceField(
                label="Taak",
                widget=forms.Select(),
                choices=taakopdracht_opties,
                required=True,
            )


class TaakAnnulerenForm(forms.Form):
    def __init__(self, *args, **kwargs):
        taakopdracht_opties = kwargs.pop("taakopdracht_opties", None)
        super().__init__(*args, **kwargs)

        if taakopdracht_opties:
            self.fields["taakopdracht"] = forms.ChoiceField(
                label="Taak",
                widget=forms.Select(),
                choices=taakopdracht_opties,
                required=True,
            )

            self.fields["omschrijving_intern"] = forms.CharField(
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
    standaard_omschrijvingen = forms.ModelChoiceField(
        queryset=StandaardExterneOmschrijving.objects.all(),
        label="Selecteer een afhandelreden",
        to_field_name="tekst",
        required=False,
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "data-testid": "testid",
                "data-meldingbehandelformulier-target": "standardTextChoice",
                "data-action": "meldingbehandelformulier#onChangeStandardTextChoice",
            }
        ),
    )
    omschrijving_extern = forms.CharField(
        label="Bericht voor de melder",
        help_text="Je kunt deze tekst aanpassen of eigen tekst toevoegen.",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "data-testid": "message",
                "rows": "4",
                "data-meldingbehandelformulier-target": "externalText",
                "data-action": "meldingbehandelformulier#onChangeExternalText",
                "name": "omschrijving_extern",
            }
        ),
        initial="Deze melding is behandeld. Bedankt voor uw inzet om Rotterdam schoon, heel en veilig te houden.",
        required=False,
        max_length=2000,
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


class LocatieAanpassenForm(forms.Form):
    omschrijving_intern = forms.CharField(
        label="Interne opmerking",
        help_text="Deze tekst wordt niet naar de melder verstuurd.",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": "4",
                "data-locatieaanpassenformulier-target": "internalText",
            }
        ),
        required=False,
    )
    geometrie = forms.CharField(
        label="Geometrie",
        widget=forms.HiddenInput(
            # Change to widget=forms.HiddenInput(),
            attrs={
                "data-locatieaanpassenformulier-target": "geometrie",
            }
        ),
        required=True,
    )
    plaatsnaam = forms.CharField(
        label="Plaatsnaam",
        widget=forms.TextInput(
            attrs={
                "data-locatieaanpassenformulier-target": "plaatsnaam",
                "readonly": "readonly",
            }
        ),
        required=True,
    )
    straatnaam = forms.CharField(
        label="Straatnaam",
        widget=forms.TextInput(
            attrs={
                "data-locatieaanpassenformulier-target": "straatnaam",
                "readonly": "readonly",
            }
        ),
        required=True,
    )
    huisnummer = forms.IntegerField(
        label="Huisnummer",
        widget=forms.TextInput(
            attrs={
                "data-locatieaanpassenformulier-target": "huisnummer",
                "readonly": "readonly",
            }
        ),
        required=True,
    )
    huisletter = forms.CharField(
        label="Huisletter",
        widget=forms.TextInput(
            attrs={
                "data-locatieaanpassenformulier-target": "huisletter",
                "readonly": "readonly",
            }
        ),
        required=False,
    )
    toevoeging = forms.CharField(
        label="Toevoeging",
        widget=forms.TextInput(
            attrs={
                "data-locatieaanpassenformulier-target": "toevoeging",
                "readonly": "readonly",
            }
        ),
        required=False,
    )
    postcode = forms.CharField(
        label="Postcode",
        widget=forms.TextInput(
            attrs={
                "data-locatieaanpassenformulier-target": "postcode",
                "readonly": "readonly",
            }
        ),
        required=True,
    )
    buurtnaam = forms.CharField(
        label="Buurtnaam",
        widget=forms.TextInput(
            attrs={
                "data-locatieaanpassenformulier-target": "buurtnaam",
                "readonly": "readonly",
            }
        ),
        required=True,
    )
    wijknaam = forms.CharField(
        label="Wijknaam",
        widget=forms.TextInput(
            attrs={
                "data-locatieaanpassenformulier-target": "wijknaam",
                "readonly": "readonly",
            }
        ),
        required=True,
    )

    def clean_geometrie(self):
        new_geometrie = self.cleaned_data.get("geometrie")
        current_geometrie = self.initial.get("geometrie", "")

        try:
            new_geometrie_dict = json.loads(new_geometrie)
        except json.JSONDecodeError:
            new_geometrie_dict = {}

        if new_geometrie_dict == current_geometrie:
            raise forms.ValidationError(
                "Het is niet toegestaan om de locatie aan te passen met dezelfde coordinaten."
            )

        return new_geometrie


class MeldingAanmakenForm(forms.Form):
    straatnaam = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
        label="Straat",
        required=True,
    )
    huisnummer = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
        label="Huisnummer",
        required=False,
    )
    buurtnaam = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
        label="Buurt",
        required=True,
    )
    wijknaam = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
        label="Wijk",
        required=True,
    )
    rd_x = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
        label="Rijksdriehoek x",
        required=True,
    )
    rd_y = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
        label="Rijksdriehoek y",
        required=True,
    )

    onderwerp = forms.ChoiceField(
        widget=forms.RadioSelect(
            attrs={
                "class": "list--form-radio-input",
            }
        ),
        label="Onderwerp",
        choices=(
            (
                "http://core.mor.local:8002/api/v1/onderwerp/grofvuil-op-straat/",
                "Grofvuil",
            ),
        ),
        required=True,
    )

    toelichting = forms.CharField(
        widget=forms.Textarea(),
        label="Toelichting",
        required=True,
    )

    bijlagen = forms.FileField(
        widget=forms.widgets.FileInput(
            attrs={
                "accept": ".jpg, .jpeg, .png, .heic",
                "data-action": "change->bijlagen#updateImageDisplay",
                "data-bijlagen-target": "bijlagenNieuw",
            }
        ),
        label="Foto's",
        required=False,
    )

    naam_melder = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
        label="Naam",
        required=True,
    )

    telefoon_melder = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "tel",
                "class": "form-control",
                "data-request-target": "phoneField",
            }
        ),
        label="Telefoonnummer",
        required=False,
    )

    email_melder = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "class": "form-control",
                "data-request-target": "emailField",
            }
        ),
        label="E-mailadres",
        required=False,
    )

    terugkoppeling_gewenst = forms.ChoiceField(
        widget=forms.RadioSelect(
            attrs={
                "class": "list--form-radio-input",
            }
        ),
        label="Is terugkoppeling gewenst?",
        choices=(
            ("1", "Ja"),
            ("0", "Nee"),
        ),
        required=True,
    )

    def get_categorie_choices(self):
        return []

    def get_verbose_value_from_field(self, fieldname, value):
        if hasattr(self.fields.get(fieldname), "choices"):
            choices_lookup = {c[0]: c[1] for c in self.fields[fieldname].choices}
            if isinstance(value, list):
                return [choices_lookup.get(v, v) for v in value]
            return choices_lookup.get(value, value)
        return value

    def _to_base64(self, file):
        binary_file = default_storage.open(file)
        binary_file_data = binary_file.read()
        base64_encoded_data = base64.b64encode(binary_file_data)
        base64_message = base64_encoded_data.decode("utf-8")
        return base64_message

    def get_onderwerp_urls(self, onderwerp_ids):
        return []

    def signaal_data(self, files=[]):
        now = timezone.localtime(timezone.now())
        data = self.cleaned_data
        data.pop("bijlagen")
        labels = {
            k: {
                "label": v.label,
                "choices": {c[0]: c[1] for c in v.choices}
                if hasattr(v, "choices")
                else None,
            }
            for k, v in self.fields.items()
        }
        choice_fields = ("terugkoppeling_gewenst",)
        for cf in choice_fields:
            data[cf] = self.get_verbose_value_from_field(cf, data[cf])

        post_data = {
            "signaal_url": "https://planr.rotterdam.nl/melding/signaal/42",
            "melder": {
                "naam": data.get("naam_melder"),
                "email": data.get("email_melder"),
                "telefoonnummer": data.get("telefoon_melder"),
            },
            "origineel_aangemaakt": now.isoformat(),
            "onderwerpen": [data.get("onderwerp", [])],
            "omschrijving_kort": data.get("toelichting", "")[:200],
            "omschrijving": data.get("toelichting", ""),
            "meta": data,
            "meta_uitgebreid": labels,
            "adressen": [
                {
                    "plaatsnaam": "Rotterdam",
                    "straatnaam": data.get("straatnaam"),
                    "huisnummer": data.get("huisnummer")
                    if data.get("huisnummer")
                    else 0,
                    "buurtnaam": data.get("buurtnaam"),
                    "wijknaam": data.get("wijknaam"),
                    "geometrie": {
                        "type": "Point",
                        "coordinates": [4.43995901, 51.93254212],
                    },
                },
            ],
        }
        try:
            post_data["adressen"][0]["geometrie"] = rd_to_wgs(
                data.get("rd_x"), data.get("rd_y")
            )
        except Exception:
            logger.error(data.get("rd_x"))
            logger.error(data.get("rd_y"))
        post_data["bijlagen"] = [{"bestand": self._to_base64(file)} for file in files]
        return post_data


class MSBLoginForm(forms.Form):
    gebruikersnummer = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
        label="Gebruikernummer",
        required=True,
    )
    wachtwoord = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
        label="Wachtwoord",
        required=True,
    )
    omgeving = forms.ChoiceField(
        widget=forms.RadioSelect(
            attrs={
                "class": "list--form-radio-input",
            }
        ),
        label="Op welke omgeving wil je inloggen",
        choices=(
            ("https://diensten-acc.rotterdam.nl", "Acceptatie"),
            ("https://diensten.rotterdam.nl", "Productie"),
        ),
        initial="https://diensten-acc.rotterdam.nl",
        required=True,
    )


class MSBMeldingZoekenForm(forms.Form):
    msb_nummer = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
        label="MSB nummer",
        required=True,
    )


# Standaard externe omschrijving forms


class StandaardExterneOmschrijvingAanpassenForm(forms.ModelForm):
    titel = forms.CharField(
        label="Afhandelreden",
        help_text="Deze tekst wordt gebruikt om de juiste standaard externe omschrijving te selecteren.",
        widget=forms.TextInput(
            attrs={
                "data-externeomschrijvingformulier-target": "externeOmschrijvingTitel",
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
                "data-action": "externeomschrijvingformulier#onChangeExterneOmschrijvingTekst",
                "name": "tekst",
            }
        ),
        label="Bericht naar melder",
        max_length=2000,
    )

    class Meta:
        model = StandaardExterneOmschrijving
        fields = ["titel", "tekst"]


class StandaardExterneOmschrijvingAanmakenForm(
    StandaardExterneOmschrijvingAanpassenForm
):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields[
        #     "titel"
        # ].help_text = "Geef een titel op voor de standaard tekst."
        # self.fields[
        #     "tekst"
        # ].help_text = "Geef een standaard tekst op van maximaal 2000 tekens. Deze tekst kan bij het afhandelen van een melding aangepast worden."


class StandaardExterneOmschrijvingSearchForm(forms.Form):
    search = forms.CharField(
        label="Zoeken",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Zoek standaard tekst"}),
    )
