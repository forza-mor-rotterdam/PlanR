import base64
import logging

from django import forms
from django.core.files.storage import default_storage
from django.utils import timezone
from utils.rd_convert import rd_to_wgs

logger = logging.getLogger(__name__)


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

TAAK_BEHANDEL_STATUS = {bo[0]: bo[3] for bo in TAAK_BEHANDEL_OPTIES}
TAAK_BEHANDEL_RESOLUTIE = {bo[0]: bo[4] for bo in TAAK_BEHANDEL_OPTIES}


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
    omschrijving_extern = forms.CharField(
        label="Bericht voor de melder",
        help_text="Je kunt deze tekst aanpassen of eigen tekst toevoegen.",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "data-testid": "message",
                "rows": "4",
                "data-meldingbehandelformulier-target": "externalText",
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
