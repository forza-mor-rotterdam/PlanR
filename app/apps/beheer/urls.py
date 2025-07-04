from apps.authenticatie.views import (
    GebruikerAanmakenView,
    GebruikerAanpassenView,
    GebruikerLijstView,
    GebruikerTerughalenView,
    GebruikerVerwijderenView,
    gebruiker_bulk_import,
)
from apps.authorisatie.views import (
    RechtengroepAanmakenView,
    RechtengroepAanpassenView,
    RechtengroepLijstView,
    RechtengroepVerwijderenView,
)
from apps.beheer.views import (
    MeldingAfhandelredenAanmakenView,
    MeldingAfhandelredenAanpassenView,
    MeldingAfhandelredenLijstView,
    MeldingAfhandelredenVerwijderenView,
    SpecificatieAanmakenView,
    SpecificatieAanpassenView,
    SpecificatieLijstView,
    SpecificatieTerughalenView,
    SpecificatieVerwijderenView,
    StandaardExterneOmschrijvingAanmakenView,
    StandaardExterneOmschrijvingAanpassenView,
    StandaardExterneOmschrijvingLijstView,
    StandaardExterneOmschrijvingVerwijderenView,
    beheer,
)
from apps.context.views import (
    ContextAanmakenView,
    ContextAanpassenView,
    ContextLijstView,
    ContextVerwijderenView,
)
from apps.release_notes.views import (
    ReleaseNoteAanmakenView,
    ReleaseNoteAanpassenView,
    ReleaseNoteListView,
    ReleaseNoteVerwijderenView,
)
from django.urls import path

urlpatterns = [
    path("", beheer, name="beheer"),
    path(
        "gebruiker/",
        GebruikerLijstView.as_view(),
        name="gebruiker_lijst",
    ),
    path(
        "gebruiker/bulk-import/",
        gebruiker_bulk_import,
        name="gebruiker_bulk_import",
    ),
    path(
        "gebruiker/aanmaken/",
        GebruikerAanmakenView.as_view(),
        name="gebruiker_aanmaken",
    ),
    path(
        "gebruiker/<int:pk>/aanpassen/",
        GebruikerAanpassenView.as_view(),
        name="gebruiker_aanpassen",
    ),
    path(
        "gebruiker/<int:pk>/verwijderen/",
        GebruikerVerwijderenView.as_view(),
        name="gebruiker_verwijderen",
    ),
    path(
        "gebruiker/<int:pk>/terughalen/",
        GebruikerTerughalenView.as_view(),
        name="gebruiker_terughalen",
    ),
    path("context/", ContextLijstView.as_view(), name="context_lijst"),
    path(
        "context/aanmaken/",
        ContextAanmakenView.as_view(),
        name="context_aanmaken",
    ),
    path(
        "context/<int:pk>/aanpassen/",
        ContextAanpassenView.as_view(),
        name="context_aanpassen",
    ),
    path(
        "context/<int:pk>/verwijderen/",
        ContextVerwijderenView.as_view(),
        name="context_verwijderen",
    ),
    path(
        "rechtengroep/",
        RechtengroepLijstView.as_view(),
        name="rechtengroep_lijst",
    ),
    path(
        "rechtengroep/aanmaken/",
        RechtengroepAanmakenView.as_view(),
        name="rechtengroep_aanmaken",
    ),
    path(
        "rechtengroep/<int:pk>/aanpassen/",
        RechtengroepAanpassenView.as_view(),
        name="rechtengroep_aanpassen",
    ),
    path(
        "rechtengroep/<int:pk>/verwijderen/",
        RechtengroepVerwijderenView.as_view(),
        name="rechtengroep_verwijderen",
    ),
    # Standaard Tekst
    path(
        "standaardtekst/",
        StandaardExterneOmschrijvingLijstView.as_view(),
        name="standaard_externe_omschrijving_lijst",
    ),
    path(
        "standaardtekst/aanmaken/",
        StandaardExterneOmschrijvingAanmakenView.as_view(),
        name="standaard_externe_omschrijving_aanmaken",
    ),
    path(
        "standaardtekst/<int:pk>/aanpassen/",
        StandaardExterneOmschrijvingAanpassenView.as_view(),
        name="standaard_externe_omschrijving_aanpassen",
    ),
    path(
        "standaardtekst/<int:pk>/verwijderen/",
        StandaardExterneOmschrijvingVerwijderenView.as_view(),
        name="standaard_externe_omschrijving_verwijderen",
    ),
    path(
        "melding-afhandelreden/",
        MeldingAfhandelredenLijstView.as_view(),
        name="melding_afhandelreden_lijst",
    ),
    path(
        "melding-afhandelreden/aanmaken/",
        MeldingAfhandelredenAanmakenView.as_view(),
        name="melding_afhandelreden_aanmaken",
    ),
    path(
        "melding-afhandelreden/<int:pk>/aanpassen/",
        MeldingAfhandelredenAanpassenView.as_view(),
        name="melding_afhandelreden_aanpassen",
    ),
    path(
        "melding-afhandelreden/<int:pk>/verwijderen/",
        MeldingAfhandelredenVerwijderenView.as_view(),
        name="melding_afhandelreden_verwijderen",
    ),
    path(
        "specificatie/",
        SpecificatieLijstView.as_view(),
        name="specificatie_lijst",
    ),
    path(
        "specificatie/aanmaken/",
        SpecificatieAanmakenView.as_view(),
        name="specificatie_aanmaken",
    ),
    path(
        "specificatie/<uuid:uuid>/aanpassen/",
        SpecificatieAanpassenView.as_view(),
        name="specificatie_aanpassen",
    ),
    path(
        "specificatie/<uuid:uuid>/verwijderen/",
        SpecificatieVerwijderenView.as_view(),
        name="specificatie_verwijderen",
    ),
    path(
        "specificatie/<uuid:uuid>/terughalen/",
        SpecificatieTerughalenView.as_view(),
        name="specificatie_terughalen",
    ),
    path(
        "release-notes/",
        ReleaseNoteListView.as_view(),
        name="release_note_lijst",
    ),
    path(
        "release-notes/aanmaken/",
        ReleaseNoteAanmakenView.as_view(),
        name="release_note_aanmaken",
    ),
    path(
        "release-notes/<int:pk>/aanpassen/",
        ReleaseNoteAanpassenView.as_view(),
        name="release_note_aanpassen",
    ),
    path(
        "release-notes/<int:pk>/verwijderen/",
        ReleaseNoteVerwijderenView.as_view(),
        name="release_note_verwijderen",
    ),
]
