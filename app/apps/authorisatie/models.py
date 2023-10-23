from django.contrib.gis.db import models


class BasisPermissie:
    naam = None
    codenaam = None


class MeldingAfhandelenPermissie(BasisPermissie):
    naam = "Melding afhandelen"
    codenaam = "melding_afhandelen"


class MeldingAanmakenPermissie(BasisPermissie):
    naam = "Melding aanmaken"
    codenaam = "melding_aanmaken"


class MeldingBekijkenPermissie(BasisPermissie):
    naam = "Melding bekijken"
    codenaam = "melding_bekijken"


class MeldingenLijstBekijkenPermissie(BasisPermissie):
    naam = "Melding lijst bekijken"
    codenaam = "melding_lijst_bekijken"


class TaakAanmakenPermissie(BasisPermissie):
    naam = "Taak aanmaken"
    codenaam = "taak_aanmaken"


class TaakAfrondenPermissie(BasisPermissie):
    naam = "Taak afronden"
    codenaam = "taak_afronden"


class TaakAnnulerenPermissie(BasisPermissie):
    naam = "Taak annuleren"
    codenaam = "taak_annuleren"


class GebruikerLijstBekijkenPermissie(BasisPermissie):
    naam = "Gebruiker lijst bekijken"
    codenaam = "gebruiker_lijst_bekijken"


class GebruikerAanmakenPermissie(BasisPermissie):
    naam = "Gebruiker aanmaken"
    codenaam = "gebruiker_aanmaken"


class GebruikerBekijkenPermissie(BasisPermissie):
    naam = "Gebruiker bekijken"
    codenaam = "gebruiker_bekijken"


class GebruikerAanpassenPermissie(BasisPermissie):
    naam = "Gebruiker aanpassen"
    codenaam = "gebruiker_aanpassen"


class GebruikerVerwijderenPermissie(BasisPermissie):
    naam = "Gebruiker verwijderen"
    codenaam = "gebruiker_verwijderen"


class GebruikersgroepToekennenPermissie(BasisPermissie):
    naam = "Gebruikersgroep toekennen/verwijderen voor een gebruiker"
    codenaam = "gebruikersgroep_toekennen_verwijderen"


class GebruikersgroepAanmakenPermissie(BasisPermissie):
    naam = "Gebruikersgroep aanmaken"
    codenaam = "gebruikersgroep_aanmaken"


class GebruikersgroepBekijkenPermissie(BasisPermissie):
    naam = "Gebruikersgroep bekijken"
    codenaam = "gebruikersgroep_bekijken"


class GebruikersgroepVerwijderenPermissie(BasisPermissie):
    naam = "Gebruikersgroep verwijderen"
    codenaam = "gebruikersgroep_verwijderen"


class BeheerBekijkenPermissie(BasisPermissie):
    naam = "Beheer bekijken"
    codenaam = "beheer_bekijken"


class MSBPermissie(BasisPermissie):
    naam = "MSB toegang"
    codenaam = "msb_toegang"


class ContextLijstBekijkenPermissie(BasisPermissie):
    naam = "Context lijst bekijken"
    codenaam = "context_lijst_bekijken"


class ContextAanmakenPermissie(BasisPermissie):
    naam = "Context aanmaken"
    codenaam = "context_aanmaken"


class ContextBekijkenPermissie(BasisPermissie):
    naam = "Context bekijken"
    codenaam = "context_bekijken"


class ContextAanpassenPermissie(BasisPermissie):
    naam = "Context aanpassen"
    codenaam = "context_aanpassen"


class ContextVerwijderenPermissie(BasisPermissie):
    naam = "Context verwijderen"
    codenaam = "context_verwijderen"


gebruikersgroep_permissies = (
    MeldingAfhandelenPermissie,
    MeldingAanmakenPermissie,
    MeldingBekijkenPermissie,
    MeldingenLijstBekijkenPermissie,
    TaakAanmakenPermissie,
    TaakAfrondenPermissie,
    GebruikerLijstBekijkenPermissie,
    GebruikerAanmakenPermissie,
    GebruikerBekijkenPermissie,
    GebruikerAanpassenPermissie,
    GebruikerVerwijderenPermissie,
    GebruikersgroepToekennenPermissie,
    GebruikersgroepAanmakenPermissie,
    GebruikersgroepBekijkenPermissie,
    GebruikersgroepVerwijderenPermissie,
    BeheerBekijkenPermissie,
    MSBPermissie,
    ContextLijstBekijkenPermissie,
    ContextAanmakenPermissie,
    ContextBekijkenPermissie,
    ContextAanpassenPermissie,
    ContextVerwijderenPermissie,
)

gebruikersgroep_permissie_opties = [
    (p.codenaam, p.naam) for p in gebruikersgroep_permissies
]


class Permissie(models.Model):
    class Meta:
        managed = False
        default_permissions = ()
        permissions = gebruikersgroep_permissie_opties
