from apps.authenticatie.managers import GebruikerManager
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models
from utils.fields import DictJSONField
from utils.models import BasisModel


class Gebruiker(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = GebruikerManager()

    def __str__(self):
        return self.email


User = get_user_model()


class Profiel(BasisModel):
    """
    Profiel model voor Gebruikers
    """

    gebruiker = models.OneToOneField(
        to=User,
        related_name="profiel",
        on_delete=models.CASCADE,
    )

    filters = DictJSONField(default=dict)
    ui_instellingen = DictJSONField(default=dict)
    context = models.ForeignKey(
        to="context.Context",
        related_name="profielen_voor_context",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def __str__(self):
        if self.gebruiker:
            return f"Profiel voor: {self.gebruiker}"
        return f"Profiel id: {self.pk}"
