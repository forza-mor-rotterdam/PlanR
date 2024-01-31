from django.contrib.gis.db import models


class BasisPermissie:
    naam = None
    codenaam = None


class MeldingAfhandelenPermissie(BasisPermissie):
    naam = "Melding afhandelen"
    codenaam = "melding_afhandelen"


class MeldingAnnulerenPermissie(BasisPermissie):
    naam = "Melding annuleren"
    codenaam = "melding_annuleren"


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


class BeheerBekijkenPermissie(BasisPermissie):
    naam = "Beheer bekijken"
    codenaam = "beheer_bekijken"


class MSBPermissie(BasisPermissie):
    naam = "MSB toegang"
    codenaam = "msb_toegang"


class ContextLijstBekijkenPermissie(BasisPermissie):
    naam = "Rol lijst bekijken"
    codenaam = "context_lijst_bekijken"


class ContextAanmakenPermissie(BasisPermissie):
    naam = "Rol aanmaken"
    codenaam = "context_aanmaken"


class ContextBekijkenPermissie(BasisPermissie):
    naam = "Rol bekijken"
    codenaam = "context_bekijken"


class ContextAanpassenPermissie(BasisPermissie):
    naam = "Rol aanpassen"
    codenaam = "context_aanpassen"


class ContextVerwijderenPermissie(BasisPermissie):
    naam = "Rol verwijderen"
    codenaam = "context_verwijderen"


class RechtengroepLijstBekijkenPermissie(BasisPermissie):
    naam = "Rechtengroep lijst bekijken"
    codenaam = "rechtengroep_lijst_bekijken"


class RechtengroepAanmakenPermissie(BasisPermissie):
    naam = "Rechtengroep aanmaken"
    codenaam = "rechtengroep_aanmaken"


class RechtengroepBekijkenPermissie(BasisPermissie):
    naam = "Rechtengroep bekijken"
    codenaam = "rechtengroep_bekijken"


class RechtengroepAanpassenPermissie(BasisPermissie):
    naam = "Rechtengroep aanpassen"
    codenaam = "rechtengroep_aanpassen"


class RechtengroepVerwijderenPermissie(BasisPermissie):
    naam = "Rechtengroep verwijderen"
    codenaam = "rechtengroep_verwijderen"


# Rechten voor Standaard Externe Omschrijvingen


class StandaardExterneOmschrijvingLijstBekijkenPermissie(BasisPermissie):
    naam = "Standaard externe omschrijving lijst bekijken"
    codenaam = "standaard_externe_omschrijving_lijst_bekijken"


class StandaardExterneOmschrijvingAanmakenPermissie(BasisPermissie):
    naam = "Standaard externe omschrijving aanmaken"
    codenaam = "standaard_externe_omschrijving_aanmaken"


class StandaardExterneOmschrijvingBekijkenPermissie(BasisPermissie):
    naam = "Standaard externe omschrijving bekijken"
    codenaam = "standaard_externe_omschrijving_bekijken"


class StandaardExterneOmschrijvingAanpassenPermissie(BasisPermissie):
    naam = "Standaard externe omschrijving aanpassen"
    codenaam = "standaard_externe_omschrijving_aanpassen"


class StandaardExterneOmschrijvingVerwijderenPermissie(BasisPermissie):
    naam = "Standaard externe omschrijving verwijderen"
    codenaam = "standaard_externe_omschrijving_verwijderen"


# Rechten voor Locatie


class LocatieAanpassenPermissie(BasisPermissie):
    naam = "Locatie aanpassen"
    codenaam = "locatie_aanpassen"


# Rechten voor Taaktype Categorie


class TaaktypeCategorieLijstBekijkenPermissie(BasisPermissie):
    naam = "Taaktype categorie lijst bekijken"
    codenaam = "taaktype_categorie_lijst_bekijken"


class TaaktypeCategorieAanmakenPermissie(BasisPermissie):
    naam = "Taaktype categorie aanmaken"
    codenaam = "taaktype_categorie_aanmaken"


class TaaktypeCategorieBekijkenPermissie(BasisPermissie):
    naam = "Taaktype categorie bekijken"
    codenaam = "taaktype_categorie_bekijken"


class TaaktypeCategorieAanpassenPermissie(BasisPermissie):
    naam = "Taaktype categorie aanpassen"
    codenaam = "taaktype_categorie_aanpassen"


class TaaktypeCategorieVerwijderenPermissie(BasisPermissie):
    naam = "Taaktype categorie verwijderen"
    codenaam = "taaktype_categorie_verwijderen"


gebruikersgroep_permissies = (
    MeldingAfhandelenPermissie,
    MeldingAnnulerenPermissie,
    MeldingAanmakenPermissie,
    MeldingBekijkenPermissie,
    MeldingenLijstBekijkenPermissie,
    TaakAanmakenPermissie,
    TaakAfrondenPermissie,
    TaakAnnulerenPermissie,
    GebruikerLijstBekijkenPermissie,
    GebruikerAanmakenPermissie,
    GebruikerBekijkenPermissie,
    GebruikerAanpassenPermissie,
    GebruikerVerwijderenPermissie,
    BeheerBekijkenPermissie,
    MSBPermissie,
    ContextLijstBekijkenPermissie,
    ContextAanmakenPermissie,
    ContextBekijkenPermissie,
    ContextAanpassenPermissie,
    ContextVerwijderenPermissie,
    RechtengroepLijstBekijkenPermissie,
    RechtengroepAanmakenPermissie,
    RechtengroepBekijkenPermissie,
    RechtengroepAanpassenPermissie,
    RechtengroepVerwijderenPermissie,
    StandaardExterneOmschrijvingLijstBekijkenPermissie,
    StandaardExterneOmschrijvingAanmakenPermissie,
    StandaardExterneOmschrijvingBekijkenPermissie,
    StandaardExterneOmschrijvingAanpassenPermissie,
    StandaardExterneOmschrijvingVerwijderenPermissie,
    LocatieAanpassenPermissie,
    TaaktypeCategorieLijstBekijkenPermissie,
    TaaktypeCategorieAanmakenPermissie,
    TaaktypeCategorieBekijkenPermissie,
    TaaktypeCategorieAanpassenPermissie,
    TaaktypeCategorieVerwijderenPermissie,
)

gebruikersgroep_permissie_opties = [
    (p.codenaam, p.naam) for p in gebruikersgroep_permissies
]
permissie_namen = {p.codenaam: p.naam for p in gebruikersgroep_permissies}


class Permissie(models.Model):
    class Meta:
        managed = False
        default_permissions = ()
        permissions = gebruikersgroep_permissie_opties
