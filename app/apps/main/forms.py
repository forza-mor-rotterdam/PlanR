import base64
import logging
import math
import uuid

from apps.context.utils import get_gebruiker_context
from apps.main.models import StandaardExterneOmschrijving, TaaktypeCategorie
from apps.main.utils import get_valide_filter_classes, get_valide_kolom_classes
from apps.services.meldingen import MeldingenService
from apps.services.onderwerpen import render_onderwerp
from apps.services.taakr import TaakRService
from django import forms
from django.core.files.storage import default_storage
from django.utils import timezone
from django_select2.forms import Select2MultipleWidget, Select2Widget
from utils.rd_convert import rd_to_wgs

logger = logging.getLogger(__name__)


class CheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = "widgets/checkbox_options_grouped.html"

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
TAAK_RESOLUTIE_NIET_GEVONDEN = "niet_gevonden"


TAAK_BEHANDEL_OPTIES = (
    (
        "ja",
        "Ja",
        "We zijn met uw melding aan de slag gegaan en hebben het probleem opgelost.",
        TAAK_STATUS_VOLTOOID,
        TAAK_RESOLUTIE_OPGELOST,
    ),
    (
        "ja",
        "Niets aangetroffen op locatie",
        "In uw melding heeft u een locatie genoemd. Op deze locatie hebben wij echter niets aangetroffen. We sluiten daarom uw melding.",
        TAAK_STATUS_VOLTOOID,
        TAAK_RESOLUTIE_NIET_GEVONDEN,
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


class PagineringRadioSelect(forms.RadioSelect):
    template_name = "widgets/paginering_radio_select.html"


class FilterForm(forms.Form):
    filter_velden = []

    # Dit veld staat komma separated zoeken toe
    q = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "list--form-text-input",
                "hideLabel": True,
                "typeOfInput": "search",
                "placeHolder": "Zoek op straatnaam, contactgegevens of MeldR-nummer",
            }
        ),
        help_text="Maak gebruik van komma's om op meerdere termen te zoeken",
        label="Zoeken",
        required=False,
    )
    foldout_states = forms.CharField(
        widget=forms.HiddenInput(
            attrs={
                "data-filter-target": "foldoutStateField",
            }
        ),
        initial="[]",
        required=False,
    )
    ordering = forms.ChoiceField(
        widget=KolommenRadioSelect(
            attrs={
                "data-action": "filter#onChangeFilter",
            }
        ),
        initial="-origineel_aangemaakt",
        required=False,
    )

    offset = forms.ChoiceField(
        widget=PagineringRadioSelect(
            attrs={
                "class": "list--form-check-input",
                "data-action": "filter#onChangeFilter",
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

    def filters(self):
        for field_name in self.fields:
            if field_name in [f.get("key") for f in self.filter_velden]:
                yield self[field_name]

    def pagina_eerste_melding(self):
        offset = int(self.data["offset"])
        return offset + 1

    def pagina_laatste_melding(self):
        limit = int(self.data["limit"])
        offset = int(self.data["offset"])
        return (
            offset + limit
            if offset + limit < self.meldingen_count
            else self.meldingen_count
        )

    def _get_offset_choices(self):
        # creates paginated choices based on offset, limit and meldingen_count
        limit = int(self.data.get("limit"))
        offset = int(self.data.get("offset"))
        page_count = math.ceil(self.meldingen_count / limit)
        current_page_zero_based = math.floor(offset / limit)
        surrounding_pages = 1
        return [
            (str(p * limit), str(p + 1))
            for p in range(0, page_count)
            # always include first page
            if p in [0]
            # always include last page
            or p in [page_count - 1]
            # include pages surrounding the current page
            or (
                p >= int(current_page_zero_based) - surrounding_pages
                and p <= int(current_page_zero_based) + surrounding_pages
            )
        ]

    def _get_ordering_choices(self, kolom_classes):
        return [
            (
                cls({}),
                [
                    (o.ordering(), o)
                    for o in [
                        cls({"ordering": "up"}),
                        cls({"ordering": "down"}),
                    ]
                ],
            )
            for cls in kolom_classes
        ]

    def _get_filter_choices(self, filter_classes, filter_options):
        return [
            {
                "key": cls.key(),
                "naam": cls.label(),
                "opties": cls(filter_options.get(cls.key(), {})).opties(),
                "aantal_actief": len(self.data.getlist(cls.key(), [])),
            }
            for cls in filter_classes
        ]

    def __init__(self, *args, **kwargs):
        gebruiker = kwargs.pop("gebruiker", None)
        gebruiker_context = get_gebruiker_context(gebruiker)
        meldingen_response_data = kwargs.pop("meldingen_data", {})
        self.meldingen_count = meldingen_response_data.get("count", 0)

        super().__init__(*args, **kwargs)

        self.filter_velden = self._get_filter_choices(
            get_valide_filter_classes(gebruiker_context),
            meldingen_response_data.get("filter_options", {}),
        )

        self.fields["offset"].choices = self._get_offset_choices()
        self.fields["ordering"].choices = self._get_ordering_choices(
            get_valide_kolom_classes(gebruiker_context)
        )

        for v in self.filter_velden:
            if opties := v.get("opties"):
                total_opties = self._count_options(opties)

            self.fields[v.get("key")] = MultipleChoiceField(
                label=f"{v.get('naam')} ({v.get('aantal_actief')}/{total_opties})",
                widget=CheckboxSelectMultiple(
                    attrs={
                        "class": "list--form-check-input",
                        "data-action": "filter#onChangeFilter",
                        "hideLabel": True,
                        "foldout_states": self.data["foldout_states"],
                        "has_group": v.get("opties", [])
                        and isinstance(v.get("opties", [])[0][1], (list, tuple)),
                    }
                ),
                choices=v.get("opties", []),
                required=False,
            )

    def _count_options(self, opties):
        count = 0
        for option in opties:
            if isinstance(option[1], (list, tuple)):
                count += len(option[1])
            else:
                count += 1
        return count


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
                "maxlength": "5000",
            }
        ),
        required=False,
        max_length=5000,
    )

    bijlagen_extra = forms.FileField(
        widget=forms.widgets.FileInput(
            attrs={
                "accept": ".jpg, .jpeg, .png, .heic",
                "data-action": "change->bijlagen#updateImageDisplay",
                "data-bijlagen-target": "bijlagenExtra",
                "multiple": "multiple",
            }
        ),
        label="Voeg één of meerdere foto's toe",
        required=False,
    )


class TaakStartenForm(forms.Form):
    afdeling = forms.ChoiceField(
        label="Filter op afdeling",
        required=False,
        widget=RadioSelect(
            attrs={
                "data-taakstartenformulier-target": "afdelingField",
            }
        ),
    )

    onderwerp_gerelateerd_taaktype = forms.ChoiceField(
        widget=RadioSelect(
            attrs={
                "data-taakstartenformulier-target": "onderwerpGerelateerdTaaktypeField",
            }
        ),
        label="Onderwerp gerelateerde taak",
        required=False,
    )

    taaktype = forms.ChoiceField(
        widget=RadioSelect(
            attrs={
                "class": "",
                "data-taakstartenformulier-target": "taaktypeField",
            }
        ),
        label="Taak",
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
        taaktype_choices = kwargs.pop("taaktypes", None)
        afdeling_choices = kwargs.pop("afdelingen", None)
        onderwerp_gerelateerde_taaktypes = kwargs.pop(
            "onderwerp_gerelateerde_taaktypes", None
        )
        super().__init__(*args, **kwargs)
        self.fields["taaktype"].choices = taaktype_choices
        self.fields["afdeling"].choices = afdeling_choices
        if onderwerp_gerelateerde_taaktypes:
            self.fields[
                "onderwerp_gerelateerd_taaktype"
            ].choices = onderwerp_gerelateerde_taaktypes
        else:
            self.fields["onderwerp_gerelateerd_taaktype"].widget = forms.HiddenInput()


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
                "multiple": "multiple",
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
                "maxlength": "5000",
            }
        ),
        required=False,
        max_length=5000,
    )

    def __init__(self, *args, **kwargs):
        taakopdracht_opties = kwargs.pop("taakopdracht_opties", None)
        super().__init__(*args, **kwargs)

        if taakopdracht_opties:
            self.fields["taakopdracht"] = forms.ChoiceField(
                label="Taak",
                widget=Select2Widget(
                    attrs={
                        "class": "select2",
                        "data-select2Modal-target": "targetField",
                    }
                ),
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
                widget=Select2Widget(
                    attrs={
                        "class": "select2",
                        "data-select2Modal-target": "targetField",
                    }
                ),
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
                        "maxlength": "5000",
                    }
                ),
                required=False,
                max_length=5000,
            )


class MeldingAfhandelenForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # Als het om een B&C formulier gaat en er geen terugkoppeling gewenst is en/of er geen email bekend is
        standaard_omschrijving_niet_weergeven = kwargs.pop(
            "standaard_omschrijving_niet_weergeven", None
        )
        super().__init__(*args, **kwargs)

        (
            self.default_standaard_omschrijving,
            _created,
        ) = StandaardExterneOmschrijving.objects.get_or_create(
            titel="Standaard afhandelreden",
            defaults={
                "tekst": "Deze melding is behandeld. Bedankt voor uw inzet om Rotterdam schoon, heel en veilig te houden."
            },
        )
        if not standaard_omschrijving_niet_weergeven:
            self.fields["standaard_omschrijvingen"] = forms.ModelChoiceField(
                queryset=StandaardExterneOmschrijving.objects.all(),
                label="Afhandelreden",
                to_field_name="tekst",
                required=True,
                widget=forms.Select(
                    attrs={
                        "class": "form-control",
                        "data-testid": "testid",
                        "data-meldingbehandelformulier-target": "standardTextChoice",
                        "data-action": "meldingbehandelformulier#onChangeStandardTextChoice",
                    }
                ),
                initial=self.default_standaard_omschrijving,
            )

            self.fields["omschrijving_extern"] = forms.CharField(
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
                        "maxlength": "1000",
                    }
                ),
                required=True,
                max_length=1000,
            )

        self.fields["omschrijving_intern"] = forms.CharField(
            label="Interne opmerking",
            help_text="Deze tekst wordt niet naar de melder verstuurd.",
            widget=forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": "4",
                    "data-meldingbehandelformulier-target": "internalText",
                    "maxlength": "5000",
                }
            ),
            required=False,
            max_length=5000,
        )


class MeldingAnnulerenForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["omschrijving_intern"] = forms.CharField(
            label="Interne opmerking",
            help_text="Deze tekst wordt niet naar de melder verstuurd.",
            widget=forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": "4",
                    "data-meldingbehandelformulier-target": "internalText",
                    "maxlength": "5000",
                }
            ),
            required=False,
            max_length=5000,
        )


class MeldingHeropenenForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["omschrijving_intern"] = forms.CharField(
            label="Interne opmerking",
            help_text="Deze tekst wordt niet naar de melder verstuurd.",
            widget=forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": "4",
                    "data-meldingbehandelformulier-target": "internalText",
                    "maxlength": "5000",
                }
            ),
            required=True,
            max_length=5000,
        )


class MeldingPauzerenForm(forms.Form):
    status = forms.ChoiceField(
        label="Wie is er om informatie gevraagd?",
        widget=forms.RadioSelect(
            attrs={
                "class": "list--form-radio-input",
            }
        ),
        choices=(
            ("wachten_melder", "De melder"),
            ("pauze", "Een collega of externe instantie"),
        ),
        required=True,
    )
    omschrijving_intern = forms.CharField(
        label="Toelichting",
        help_text="Omschrijf de informatie die nodig is om de melding op te pakken.",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": "4",
                "maxlength": "5000",
            }
        ),
        required=False,
        max_length=5000,
    )


class MeldingHervattenForm(forms.Form):
    omschrijving_intern = forms.CharField(
        label="Ontvangen informatie",
        help_text="Als je informatie ontvangen hebt kun je die hier omschrijven.",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": "4",
                "maxlength": "5000",
            }
        ),
        required=False,
        max_length=5000,
    )


class MeldingSpoedForm(forms.Form):
    urgentie = forms.FloatField(
        widget=forms.HiddenInput(),
        required=True,
    )

    omschrijving_intern = forms.CharField(
        label="Interne opmerking",
        help_text="Deze tekst wordt niet naar de melder verstuurd.",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": "4",
                "maxlength": "5000",
            }
        ),
        required=False,
        max_length=5000,
    )

    def submit_label(self):
        return (
            "Geef melding spoed-status"
            if self.initial["urgentie"] >= 0.5
            else "Verwijder spoed-status"
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
                "maxlength": "5000",
            }
        ),
        required=False,
        max_length=5000,
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
        widget=forms.HiddenInput(
            attrs={
                "data-locatieaanpassenformulier-target": "plaatsnaam",
            }
        ),
        required=True,
    )
    straatnaam = forms.CharField(
        widget=forms.HiddenInput(
            attrs={
                "data-locatieaanpassenformulier-target": "straatnaam",
            }
        ),
        required=True,
    )
    huisnummer = forms.IntegerField(
        widget=forms.HiddenInput(
            attrs={
                "data-locatieaanpassenformulier-target": "huisnummer",
            }
        ),
        required=True,
    )
    huisletter = forms.CharField(
        widget=forms.HiddenInput(
            attrs={
                "data-locatieaanpassenformulier-target": "huisletter",
            }
        ),
        required=False,
    )
    toevoeging = forms.CharField(
        widget=forms.HiddenInput(
            attrs={
                "data-locatieaanpassenformulier-target": "toevoeging",
            }
        ),
        required=False,
    )
    postcode = forms.CharField(
        widget=forms.HiddenInput(
            attrs={
                "data-locatieaanpassenformulier-target": "postcode",
            }
        ),
        required=False,
    )
    wijknaam = forms.CharField(
        widget=forms.HiddenInput(
            attrs={
                "data-locatieaanpassenformulier-target": "wijknaam",
            }
        ),
        required=True,
    )
    buurtnaam = forms.CharField(
        widget=forms.HiddenInput(
            attrs={
                "data-locatieaanpassenformulier-target": "buurtnaam",
            }
        ),
        required=True,
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
    huisletter = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
        label="Huisletter",
        required=False,
        max_length=1,
    )
    toevoeging = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
        label="Toevoeging",
        required=False,
        max_length=4,
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
    buurtnaam = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
        label="Buurt",
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
        choices=(),
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
                "multiple": "multiple",
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
    melding = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
        label="Moeder melding id",
        help_text="Deze melding als dubbele melding aanmaken",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        kwargs.get("instance")
        super().__init__(*args, **kwargs)
        onderwerp_alias_list = (
            MeldingenService().onderwerp_alias_list().get("results", [])
        )
        choices = [
            (
                onderwerp_alias.get("bron_url"),
                render_onderwerp(
                    onderwerp_alias.get("bron_url"), onderwerp_alias.get("pk")
                ),
            )
            for onderwerp_alias in onderwerp_alias_list
        ]
        self.fields["onderwerp"].choices = choices

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
                "choices": (
                    {c[0]: c[1] for c in v.choices} if hasattr(v, "choices") else None
                ),
            }
            for k, v in self.fields.items()
        }
        choice_fields = ("terugkoppeling_gewenst",)
        for cf in choice_fields:
            data[cf] = self.get_verbose_value_from_field(cf, data[cf])
        bron_signaal_id = str(uuid.uuid4())
        post_data = {
            "signaal_url": f"https://planr.rotterdam.nl/melding/signaal/{bron_signaal_id}",
            "melder": {
                "naam": data.get("naam_melder"),
                "email": data.get("email_melder"),
                "telefoonnummer": data.get("telefoon_melder"),
            },
            "bron_id": "PlanR",
            "bron_signaal_id": bron_signaal_id,
            "origineel_aangemaakt": now.isoformat(),
            "onderwerpen": [{"bron_url": data.get("onderwerp", [])}],
            "omschrijving_melder": data.get("toelichting", "")[:500],
            "aanvullende_informatie": data.get("aanvullende_informatie", "")[:5000],
            "meta": data,
            "meta_uitgebreid": labels,
            "adressen": [
                {
                    "plaatsnaam": "Rotterdam",
                    "straatnaam": data.get("straatnaam"),
                    "huisnummer": data.get("huisnummer", 0),
                    "huisletter": data.get("huisletter"),
                    "toevoeging": data.get("toevoeging"),
                    "wijknaam": data.get("wijknaam"),
                    "buurtnaam": data.get("buurtnaam"),
                    "geometrie": {
                        "type": "Point",
                        "coordinates": [4.43995901, 51.93254212],
                    },
                },
            ],
        }
        if data.get("melding"):
            post_data.update({"melding": data.get("melding")})
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
        max_length=1000,
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


# Taaktype categorie forms


class TaaktypeCategorieAanpassenForm(forms.ModelForm):
    taaktypes = forms.MultipleChoiceField(
        choices=[],  # We'll set this dynamically in the form's __init__ method
        widget=Select2MultipleWidget(attrs={"class": "select2"}),
    )

    class Meta:
        model = TaaktypeCategorie
        fields = ["naam", "taaktypes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["taaktypes"].choices = self.get_taaktypes_choices()

    def get_taaktypes_choices(self):
        alle_taaktypes = TaakRService().get_taaktypes()

        current_taaktypes = (
            [
                (
                    taaktype.get("_links", {}).get("taakapplicatie_taaktype_url"),
                    taaktype.get("omschrijving"),
                )
                for taaktype in alle_taaktypes
                if taaktype.get("_links", {}).get("taakapplicatie_taaktype_url")
                in self.instance.taaktypes
            ]
            if self.instance
            else []
        )

        alle_taaktypes_urls = [
            taaktype.get("_links", {}).get("taakapplicatie_taaktype_url")
            for taaktype in alle_taaktypes
        ]

        unused_taaktypes = [
            (
                taaktype.get("_links", {}).get("taakapplicatie_taaktype_url"),
                taaktype.get("omschrijving"),
            )
            for taaktype, taaktype_url in zip(alle_taaktypes, alle_taaktypes_urls)
            if not TaaktypeCategorie.objects.filter(
                taaktypes__contains=[taaktype_url]
            ).exists()
        ]

        return unused_taaktypes + current_taaktypes


class TaaktypeCategorieAanmakenForm(TaaktypeCategorieAanpassenForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields[
        #     "titel"
        # ].help_text = "Geef een titel op voor de standaard tekst."
        # self.fields[
        #     "tekst"
        # ].help_text = "Geef een standaard tekst op van maximaal 2000 tekens. Deze tekst kan bij het afhandelen van een melding aangepast worden."


class TaaktypeCategorieSearchForm(forms.Form):
    search = forms.CharField(
        label="Zoeken",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Zoek taaktype categorie"}),
    )
