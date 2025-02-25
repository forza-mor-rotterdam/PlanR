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


class MeldingHeropenenPermissie(BasisPermissie):
    naam = "Melding heropenen"
    codenaam = "melding_heropenen"


class MeldingAanmakenPermissie(BasisPermissie):
    naam = "Melding aanmaken"
    codenaam = "melding_aanmaken"


class MeldingBekijkenPermissie(BasisPermissie):
    naam = "Melding bekijken"
    codenaam = "melding_bekijken"


class MeldingenLijstBekijkenPermissie(BasisPermissie):
    naam = "Melding lijst bekijken"
    codenaam = "melding_lijst_bekijken"


class MeldingenPauzerenPermissie(BasisPermissie):
    naam = "Melding pauzeren"
    codenaam = "melding_pauzeren"


class MeldingenHervattenPermissie(BasisPermissie):
    naam = "Melding hervatten"
    codenaam = "melding_hervatten"


class MeldingenSpoedVeranderenPermissie(BasisPermissie):
    naam = "Melding spoed veranderen"
    codenaam = "melding_spoed_veranderen"


class TaakAanmakenPermissie(BasisPermissie):
    naam = "Taak aanmaken"
    codenaam = "taak_aanmaken"


class TaakAfrondenPermissie(BasisPermissie):
    naam = "Taak afronden"
    codenaam = "taak_afronden"


class TaakAnnulerenPermissie(BasisPermissie):
    naam = "Taak annuleren"
    codenaam = "taak_annuleren"


class MedewerkerGegevensBekijkenPermissie(BasisPermissie):
    naam = "Medewerker gegevens bekijken"
    codenaam = "medewerker_gegevens_bekijken"


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


class GebruikerTerughalenPermissie(BasisPermissie):
    naam = "Gebruiker terughalen"
    codenaam = "gebruiker_terughalen"


class BeheerBekijkenPermissie(BasisPermissie):
    naam = "Beheer bekijken"
    codenaam = "beheer_bekijken"


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


# Rechten voor Standaard Teksten


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


# Rechten voor release notes
class ReleaseNoteLijstBekijkenPermissie(BasisPermissie):
    naam = "Release notes bekijken"
    codenaam = "release_note_lijst_bekijken"


class ReleaseNoteAanmakenPermissie(BasisPermissie):
    naam = "Release note aanmaken"
    codenaam = "release_note_aanmaken"


class ReleaseNoteBekijkenPermissie(BasisPermissie):
    naam = "Release note bekijken"
    codenaam = "release_note_bekijken"


class ReleaseNoteAanpassenPermissie(BasisPermissie):
    naam = "Release note aanpassen"
    codenaam = "release_note_aanpassen"


class ReleaseNoteVerwijderenPermissie(BasisPermissie):
    naam = "Release note verwijderen"
    codenaam = "release_note_verwijderen"


class DashboardBekijkenPermissie(BasisPermissie):
    naam = "Dashboard bekijken"
    codenaam = "dashboard_bekijken"


gebruikersgroep_permissies = (
    MeldingAfhandelenPermissie,
    MeldingAnnulerenPermissie,
    MeldingHeropenenPermissie,
    MeldingAanmakenPermissie,
    MeldingBekijkenPermissie,
    MeldingenLijstBekijkenPermissie,
    MeldingenPauzerenPermissie,
    MeldingenHervattenPermissie,
    MeldingenSpoedVeranderenPermissie,
    TaakAanmakenPermissie,
    TaakAfrondenPermissie,
    TaakAnnulerenPermissie,
    MedewerkerGegevensBekijkenPermissie,
    GebruikerLijstBekijkenPermissie,
    GebruikerAanmakenPermissie,
    GebruikerBekijkenPermissie,
    GebruikerAanpassenPermissie,
    GebruikerVerwijderenPermissie,
    GebruikerTerughalenPermissie,
    BeheerBekijkenPermissie,
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
    ReleaseNoteLijstBekijkenPermissie,
    ReleaseNoteAanmakenPermissie,
    ReleaseNoteBekijkenPermissie,
    ReleaseNoteAanpassenPermissie,
    ReleaseNoteVerwijderenPermissie,
    DashboardBekijkenPermissie,
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
