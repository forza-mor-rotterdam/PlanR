from apps.context.models import Context
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

Gebruiker = get_user_model()


class GebruikerAanpassenForm(forms.ModelForm):
    context = forms.ModelChoiceField(
        queryset=Context.objects.all(),
        label="UI groep",
        required=True,
    )
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label="Rechten groep",
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
