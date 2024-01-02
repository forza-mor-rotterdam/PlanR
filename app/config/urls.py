from apps.authenticatie.views import (
    GebruikerAanmakenView,
    GebruikerAanpassenView,
    GebruikerLijstView,
    gebruiker_bulk_import,
)
from apps.authorisatie.views import (
    RechtengroepAanmakenView,
    RechtengroepAanpassenView,
    RechtengroepLijstView,
    RechtengroepVerwijderenView,
)
from apps.beheer.views import beheer
from apps.context.views import (
    ContextAanmakenView,
    ContextAanpassenView,
    ContextLijstView,
    ContextVerwijderenView,
)
from apps.main.views import (
    StandaardExterneOmschrijvingAanmakenView,
    StandaardExterneOmschrijvingAanpassenView,
    StandaardExterneOmschrijvingLijstView,
    StandaardExterneOmschrijvingVerwijderenView,
    account,
    http_404,
    http_500,
    informatie_toevoegen,
    locatie_aanpassen,
    melding_aanmaken,
    melding_afhandelen,
    melding_annuleren,
    melding_detail,
    melding_lijst,
    melding_pdf_download,
    melding_verzonden,
    meldingen_bestand,
    msb_importeer_melding,
    msb_login,
    msb_melding_zoeken,
    root,
    taak_afronden,
    taak_annuleren,
    taak_starten,
)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from rest_framework.authtoken import views

urlpatterns = [
    path("", root, name="root"),
    path("account/", account, name="account"),
    path("api-token-auth/", views.obtain_auth_token),
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("melding/", melding_lijst, name="melding_lijst"),
    path("melding/<uuid:id>/", melding_detail, name="melding_detail"),
    path("health/", include("health_check.urls")),
    path("msb/login/", msb_login, name="msb_login"),
    path("msb/zoeken/", msb_melding_zoeken, name="msb_melding_zoeken"),
    path("msb/importeer/", msb_importeer_melding, name="msb_importeer_melding"),
    path(
        "part/melding/<uuid:id>/afhandelen/",
        melding_afhandelen,
        name="melding_afhandelen",
    ),
    path(
        "part/melding/<uuid:id>/annuleren/",
        melding_annuleren,
        name="melding_annuleren",
    ),
    path(
        "part/melding/<uuid:id>/taakstarten/",
        taak_starten,
        name="taak_starten",
    ),
    path(
        "part/melding/<uuid:melding_uuid>/taak-afronden/",
        taak_afronden,
        name="taak_afronden",
    ),
    path(
        "part/melding/<uuid:melding_uuid>/taak-annuleren/",
        taak_annuleren,
        name="taak_annuleren",
    ),
    path(
        "part/melding/<uuid:id>/informatie-toevoegen/",
        informatie_toevoegen,
        name="informatie_toevoegen",
    ),
    path(
        "download/melding/<uuid:id>/pdf/",
        melding_pdf_download,
        name="melding_pdf_download",
    ),
    path("melding/aanmaken", melding_aanmaken, name="melding_aanmaken"),
    path(
        "melding/verzonden/<uuid:signaal_uuid>/",
        melding_verzonden,
        name="melding_verzonden",
    ),
    path("beheer/", beheer, name="beheer"),
    path(
        "beheer/gebruiker/",
        GebruikerLijstView.as_view(),
        name="gebruiker_lijst",
    ),
    path(
        "beheer/gebruiker/bulk-import/",
        gebruiker_bulk_import,
        name="gebruiker_bulk_import",
    ),
    path(
        "beheer/gebruiker/aanmaken/",
        GebruikerAanmakenView.as_view(),
        name="gebruiker_aanmaken",
    ),
    path(
        "beheer/gebruiker/<int:pk>/aanpassen/",
        GebruikerAanpassenView.as_view(),
        name="gebruiker_aanpassen",
    ),
    path("beheer/context/", ContextLijstView.as_view(), name="context_lijst"),
    path(
        "beheer/context/aanmaken/",
        ContextAanmakenView.as_view(),
        name="context_aanmaken",
    ),
    path(
        "beheer/context/<int:pk>/aanpassen/",
        ContextAanpassenView.as_view(),
        name="context_aanpassen",
    ),
    path(
        "beheer/context/<int:pk>/verwijderen/",
        ContextVerwijderenView.as_view(),
        name="context_verwijderen",
    ),
    path(
        "beheer/rechtengroep/",
        RechtengroepLijstView.as_view(),
        name="rechtengroep_lijst",
    ),
    path(
        "beheer/rechtengroep/aanmaken/",
        RechtengroepAanmakenView.as_view(),
        name="rechtengroep_aanmaken",
    ),
    path(
        "beheer/rechtengroep/<int:pk>/aanpassen/",
        RechtengroepAanpassenView.as_view(),
        name="rechtengroep_aanpassen",
    ),
    path(
        "beheer/rechtengroep/<int:pk>/verwijderen/",
        RechtengroepVerwijderenView.as_view(),
        name="rechtengroep_verwijderen",
    ),
    # Standaard externe omschrijving
    path(
        "beheer/standaardtekst/",
        StandaardExterneOmschrijvingLijstView.as_view(),
        name="standaard_externe_omschrijving_lijst",
    ),
    path(
        "beheer/standaardtekst/aanmaken/",
        StandaardExterneOmschrijvingAanmakenView.as_view(),
        name="standaard_externe_omschrijving_aanmaken",
    ),
    path(
        "beheer/standaardtekst/<int:pk>/aanpassen/",
        StandaardExterneOmschrijvingAanpassenView.as_view(),
        name="standaard_externe_omschrijving_aanpassen",
    ),
    path(
        "beheer/standaardtekst/<int:pk>/verwijderen/",
        StandaardExterneOmschrijvingVerwijderenView.as_view(),
        name="standaard_externe_omschrijving_verwijderen",
    ),
    ### Locatie
    path(
        "part/melding/<uuid:id>/locatie_aanpassen/",
        locatie_aanpassen,
        name="locatie_aanpassen",
    ),
    re_path(r"media/", meldingen_bestand, name="meldingen_bestand"),
]

if settings.OIDC_ENABLED:
    urlpatterns += [
        path("oidc/", include("mozilla_django_oidc.urls")),
        path(
            "admin/login/",
            RedirectView.as_view(
                url="/oidc/authenticate/?next=/admin/",
                permanent=False,
            ),
            name="admin_login",
        ),
        path(
            "admin/logout/",
            RedirectView.as_view(
                url="/oidc/logout/?next=/admin/",
                permanent=False,
            ),
            name="admin_logout",
        ),
        path("admin/", admin.site.urls),
    ]
else:
    urlpatterns += [
        path("admin/", admin.site.urls),
    ]


if settings.DEBUG:
    urlpatterns += [
        path("404/", http_404, name="404"),
        path("500/", http_500, name="500"),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
