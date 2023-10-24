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
    UserModel = get_user_model()
    gebruiker = UserModel.objects.filter(email=value).first()
    if gebruiker:
        return gebruikersnaam_basis(gebruiker)
    return value
