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
    emailadressen = forms.CharField(
        widget=forms.Textarea(),
        label="E-mailaddressen",
        help_text="Komma gescheiden email adressen van de gebruikers (123456@rotterdam, 234567@rotterdam)",
        required=True,
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

    def clean_emailadressen(self):
        emailadressen = self.cleaned_data["emailadressen"].split(",")
        valide_emailadressen = []

        def check_emailadres(emailadres):
            is_emailadres = True
            try:
                validate_email(emailadres)
            except ValidationError:
                is_emailadres = False
            bestaat_niet = not Gebruiker.objects.all().filter(email=emailadres)
            if is_emailadres and bestaat_niet:
                valide_emailadressen.append(emailadres)
            return {
                "bestaat_niet": bestaat_niet,
                "is_emailadres": is_emailadres,
                "emailadres": emailadres,
            }

        clean_emaillijst = [
            check_emailadres(emailadres.strip())
            for emailadres in emailadressen
            if emailadres.strip()
        ]
        return {
            "validate_resultaat": clean_emaillijst,
            "valide_emailadressen": valide_emailadressen,
        }

    def submit(self):
        if not self.cleaned_data:
            return
        aangemaakte_gebruikers = Gebruiker.objects.bulk_create(
            [
                Gebruiker(
                    email=emailadres,
                )
                for emailadres in self.cleaned_data.get("emailadressen", {}).get(
                    "valide_emailadressen", []
                )
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
