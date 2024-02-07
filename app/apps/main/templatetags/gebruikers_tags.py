from apps.services.meldingen import MeldingenService
from django import template
from django.contrib.auth import get_user_model
from utils.diversen import gebruikersnaam as gebruikersnaam_basis

register = template.Library()


@register.filter
def gebruikersnaam(value):
    return gebruikersnaam_basis(value)


@register.filter
def gebruiker_middels_email(value):
    if not value:
        return ""

    gebruiker_response = MeldingenService().get_gebruiker(
        gebruiker_email=value,
    )
    if gebruiker_response.status_code == 200:
        gebruiker = gebruiker_response.json()
        first_name = gebruiker.get("first_name")
        last_name = gebruiker.get("last_name")
        name = [n for n in [first_name, last_name] if n]
        if name:
            return " ".join(name)

    UserModel = get_user_model()
    gebruiker = UserModel.objects.filter(email=value).first()
    if gebruiker:
        return gebruikersnaam_basis(gebruiker)
    return value
