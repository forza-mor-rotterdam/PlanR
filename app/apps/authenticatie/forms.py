import csv
from io import StringIO

from apps.authenticatie.models import Profiel
from apps.context.models import Context
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

Gebruiker = get_user_model()


class GebruikerAanpassenForm(forms.ModelForm):
    context = forms.ModelChoiceField(
        queryset=Context.objects.all(),
        label="Rol",
        required=True,
    )
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label="Rechtengroep",
        required=False,
    )

    class Meta:
        model = Gebruiker
        fields = ("telefoonnummer", "first_name", "last_name", "group", "context")


class GebruikerAanmakenForm(GebruikerAanpassenForm):
    class Meta:
        model = Gebruiker
        fields = (
            "email",
            "telefoonnummer",
            "first_name",
            "last_name",
            "group",
            "context",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[
            "email"
        ].help_text = "Gebruik altijd het e-mailadres van de gemeente."
        self.fields[
            "context"
        ].help_text = (
            "Bestaat de juiste rol voor deze gebruiker niet, maak deze eerst aan."
        )
        self.fields[
            "group"
        ].help_text = "Bestaat de juiste rechtengroep voor deze gebruiker niet, maak deze eerst aan."


class GebruikerBulkImportForm(forms.Form):
    csv_file = forms.FileField(
        widget=forms.FileInput(
            attrs={
                "data-action": "change->bijlagen#updateImageDisplay",
                "accept": ".csv",
                "required_css_class": "required",
                "button_text": "CSV bestand",
            }
        ),
        label="CSV upload",
    )
    context = forms.ModelChoiceField(
        widget=forms.Select(attrs={"class": "form-control"}),
        queryset=Context.objects.all(),
        label="Rol",
        required=True,
    )
    group = forms.ModelChoiceField(
        widget=forms.Select(attrs={"class": "form-control"}),
        queryset=Group.objects.all(),
        label="Rechtengroep",
        required=True,
    )

    def clean_csv_file(self):
        all_rows = []
        valid_rows = []
        csv_file = self.cleaned_data["csv_file"]
        csv_fo = StringIO(csv_file.read().decode("utf-8"))
        spamreader = csv.reader(csv_fo, delimiter=";", quotechar="|")
        valid_checked_rows_email = []
        for row in spamreader:
            default_row = [row[r] if r < len(row) else None for r in range(0, 4)]
            errors = []
            if default_row[0] in valid_checked_rows_email:
                errors.append(
                    "Er is al een gebruiker met dit e-mailadres in deze lijst aanwezig"
                )
            row_is_not_valid = self.validate_row(default_row, errors)
            if not row_is_not_valid:
                valid_rows.append(default_row)
                valid_checked_rows_email.append(default_row[0])
            default_row.append(row_is_not_valid)
            all_rows.append(default_row)
        return {
            "all_rows": all_rows,
            "valid_rows": valid_rows,
        }

    def validate_row(self, row, errors=[]):
        email = row[0]
        first_name = row[1]
        last_name = row[2]
        telefoonnummer = row[3]
        try:
            validate_email(email.strip())
        except ValidationError:
            errors.append(f"{email} is geen e-mailadres")
        if Gebruiker.objects.all().filter(email=email):
            errors.append("Een gebruiker met dit e-mailadres bestaat reeds")
        if first_name and len(first_name) > 150:
            errors.append("voornaam mag niet langer zijn dan 150 karakters")
        if last_name and len(last_name) > 150:
            errors.append("achternaam mag niet langer zijn dan 150 karakters")
        if telefoonnummer and len(telefoonnummer) > 17:
            errors.append("telefoonnummer mag niet langer zijn dan 17 karakters")
        return ", ".join(errors)

    def submit(self, valid_rows):
        gebruiker_fieldnames = [
            "email",
            "first_name",
            "last_name",
            "telefoonnummer",
        ]
        aangemaakte_gebruikers = Gebruiker.objects.bulk_create(
            [
                Gebruiker(**{f: row[i] for i, f in enumerate(gebruiker_fieldnames)})
                for row in valid_rows
            ]
        )
        for gebruiker in aangemaakte_gebruikers:
            gebruiker.groups.add(self.cleaned_data.get("group"))
            Profiel.objects.create(
                gebruiker=gebruiker,
                context=self.cleaned_data.get("context"),
            )
            gebruiker.save()
        return aangemaakte_gebruikers


class GebruikerProfielForm(forms.ModelForm):
    telefoonnummer = forms.CharField(
        label="Telefoonnummer",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    first_name = forms.CharField(
        label="Voornaam",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    last_name = forms.CharField(
        label="Achternaam",
        required=False,
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    class Meta:
        model = Gebruiker
        fields = ("telefoonnummer", "first_name", "last_name")
