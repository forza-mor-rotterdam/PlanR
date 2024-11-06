from apps.authenticatie.views import (
    GebruikerAanmakenView,
    GebruikerAanpassenView,
    GebruikerLijstView,
    GebruikerProfielView,
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
from apps.dashboard.views import (
    MeldingenAfgehandeld,
    NieuweMeldingen,
    NieuweTaakopdrachten,
    TaaktypeAantallen,
)
from apps.health.views import healthz
from apps.main.views import (
    LoginView,
    LogoutView,
    StandaardExterneOmschrijvingAanmakenView,
    StandaardExterneOmschrijvingAanpassenView,
    StandaardExterneOmschrijvingLijstView,
    StandaardExterneOmschrijvingVerwijderenView,
    TaaktypeCategorieAanmakenView,
    TaaktypeCategorieAanpassenView,
    TaaktypeCategorieLijstView,
    TaaktypeCategorieVerwijderenView,
    clear_melding_token_from_cache,
)
from apps.main.views import dashboard as dashboard_mock
from apps.main.views import (
    gebruiker_info,
    http_403,
    http_404,
    http_500,
    informatie_toevoegen,
    locatie_aanpassen,
    melding_aanmaken,
    melding_afhandelen,
    melding_annuleren,
    melding_detail,
    melding_heropenen,
    melding_hervatten,
    melding_lijst,
    melding_next,
    melding_pauzeren,
    melding_pdf_download,
    melding_spoed_veranderen,
    melding_verzonden,
    meldingen_bestand,
    msb_importeer_melding,
    msb_login,
    msb_melding_zoeken,
    publiceer_topic,
    root,
    sidesheet_actueel,
    taak_afronden,
    taak_annuleren,
    taak_starten,
)
from apps.release_notes.views import (
    NotificatieLijstViewPublic,
    NotificatieVerwijderViewPublic,
    ReleaseNoteAanmakenView,
    ReleaseNoteAanpassenView,
    ReleaseNoteDetailView,
    ReleaseNoteListView,
    ReleaseNoteListViewPublic,
    ReleaseNoteVerwijderenView,
)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from django_select2 import urls as select2_urls
from rest_framework.authtoken import views

urlpatterns = [
    path("", root, name="root"),
    path("api-token-auth/", views.obtain_auth_token),
    path(
        "admin/clear-melding-token-from-cache/",
        clear_melding_token_from_cache,
        name="clear_melding_token_from_cache",
    ),
    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),
    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),
    path("melding/", melding_lijst, name="melding_lijst"),
    path("melding/<uuid:id>/", melding_detail, name="melding_detail"),
    path(
        "melding/<uuid:id>/volgende/",
        melding_next,
        {"richting": 1},
        name="melding_next_volgend",
    ),
    path(
        "melding/<uuid:id>/vorige/",
        melding_next,
        {"richting": -1},
        name="melding_next_vorige",
    ),
    path("publiceer-topic/<uuid:id>/", publiceer_topic, name="publiceer_topic"),
    path("health/", include("health_check.urls")),
    path("healthz/", healthz, name="healthz"),
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
        "melding/<uuid:id>/pauzeren/",
        melding_pauzeren,
        name="melding_pauzeren",
    ),
    path(
        "melding/<uuid:id>/hervatten/",
        melding_hervatten,
        name="melding_hervatten",
    ),
    path(
        "melding/<uuid:id>/heropenen/",
        melding_heropenen,
        name="melding_heropenen",
    ),
    path(
        "melding/<uuid:id>/spoed/",
        melding_spoed_veranderen,
        name="melding_spoed_veranderen",
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
    # Standaard Tekst
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
    # Taaktype categorie
    path(
        "beheer/taaktype-categorie/",
        TaaktypeCategorieLijstView.as_view(),
        name="taaktype_categorie_lijst",
    ),
    path(
        "beheer/taaktype-categorie/aanmaken/",
        TaaktypeCategorieAanmakenView.as_view(),
        name="taaktype_categorie_aanmaken",
    ),
    path(
        "beheer/taaktype-categorie/<int:pk>/aanpassen/",
        TaaktypeCategorieAanpassenView.as_view(),
        name="taaktype_categorie_aanpassen",
    ),
    path(
        "beheer/taaktype-categorie/<int:pk>/verwijderen/",
        TaaktypeCategorieVerwijderenView.as_view(),
        name="taaktype_categorie_verwijderen",
    ),
    # Notificaties
    path(
        "notificaties/",
        NotificatieLijstViewPublic.as_view(),
        name="notificatie_lijst_public",
    ),
    path(
        "notificatie/<int:pk>/verwijderen/",
        NotificatieVerwijderViewPublic.as_view(),
        name="notificatie_verwijderen_public",
    ),
    # Release notes
    path(
        "release-notes/",
        ReleaseNoteListViewPublic.as_view(),
        name="release_note_lijst_public",
    ),
    path(
        "release-notes/<int:pk>/",
        ReleaseNoteDetailView.as_view(),
        name="release_note_detail",
    ),
    path(
        "beheer/release-notes/",
        ReleaseNoteListView.as_view(),
        name="release_note_lijst",
    ),
    path(
        "beheer/release-notes/aanmaken/",
        ReleaseNoteAanmakenView.as_view(),
        name="release_note_aanmaken",
    ),
    path(
        "beheer/release-notes/<int:pk>/aanpassen/",
        ReleaseNoteAanpassenView.as_view(),
        name="release_note_aanpassen",
    ),
    path(
        "beheer/release-notes/<int:pk>/verwijderen/",
        ReleaseNoteVerwijderenView.as_view(),
        name="release_note_verwijderen",
    ),
    # Gebruikers
    path(
        "gebruiker/gebruiker_info/<str:gebruiker_email>/",
        gebruiker_info,
        name="gebruiker_info",
    ),
    path(
        "gebruiker/profiel/",
        GebruikerProfielView.as_view(),
        name="gebruiker_profiel",
    ),
    # Dashboard
    path(
        "dashboard-mock/",
        dashboard_mock,
        name="dashboard_mock",
    ),
    # sidesheet
    path(
        "sidesheet-actueel/",
        sidesheet_actueel,
        name="sidesheet_actueel",
    ),
    ### Locatie
    path(
        "part/melding/<uuid:id>/locatie_aanpassen/",
        locatie_aanpassen,
        name="locatie_aanpassen",
    ),
    path("select2/", include(select2_urls)),
    re_path(r"core/media/", meldingen_bestand, name="meldingen_bestand"),
    # path("dashboard/", dashboard, name="dashboard"),
    re_path(
        r"^dashboard/$",
        NieuweMeldingen.as_view(),
        kwargs={"type": "meldingen", "status": "nieuw"},
        name="dashboard",
    ),
    re_path(
        r"^dashboard/(?P<jaar>\d{4})/$",
        NieuweMeldingen.as_view(periode="jaar"),
        kwargs={"type": "meldingen", "status": "nieuw"},
        name="dashboard",
    ),
    # jaren
    re_path(
        r"^dashboard/(?P<jaar>\d{4})/(?P<type>meldingen)/(?P<status>nieuw)/$",
        NieuweMeldingen.as_view(periode="jaar"),
        kwargs={"type": "meldingen", "status": "nieuw"},
        name="dashboard",
    ),
    re_path(
        r"^dashboard/(?P<jaar>\d{4})/(?P<type>meldingen)/(?P<status>afgehandeld)/$",
        MeldingenAfgehandeld.as_view(periode="jaar"),
        kwargs={"type": "meldingen", "status": "afgehandeld"},
        name="dashboard",
    ),
    re_path(
        r"^dashboard/(?P<jaar>\d{4})/(?P<type>taken)/(?P<status>aantallen)/$",
        TaaktypeAantallen.as_view(periode="jaar"),
        kwargs={"type": "taken", "status": "aantallen"},
        name="dashboard",
    ),
    re_path(
        r"^dashboard/(?P<jaar>\d{4})/(?P<type>taken)/(?P<status>nieuw)/$",
        NieuweTaakopdrachten.as_view(periode="jaar"),
        kwargs={"type": "taken", "status": "nieuw"},
        name="dashboard",
    ),
    # weken
    re_path(
        r"^dashboard/(?P<jaar>\d{4})/week/(?P<week>\d{2})/(?P<type>meldingen)/(?P<status>nieuw)/$",
        NieuweMeldingen.as_view(periode="week"),
        kwargs={"type": "meldingen", "status": "nieuw"},
        name="dashboard",
    ),
    re_path(
        r"^dashboard/(?P<jaar>\d{4})/week/(?P<week>\d{2})/(?P<type>meldingen)/(?P<status>afgehandeld)/$",
        MeldingenAfgehandeld.as_view(periode="week"),
        kwargs={"type": "meldingen", "status": "afgehandeld"},
        name="dashboard",
    ),
    re_path(
        r"^dashboard/(?P<jaar>\d{4})/week/(?P<week>\d{2})/(?P<type>taken)/(?P<status>aantallen)/$",
        TaaktypeAantallen.as_view(periode="week"),
        kwargs={"type": "taken", "status": "aantallen"},
        name="dashboard",
    ),
    re_path(
        r"^dashboard/(?P<jaar>\d{4})/week/(?P<week>\d{2})/(?P<type>taken)/(?P<status>nieuw)/$",
        NieuweTaakopdrachten.as_view(periode="week"),
        kwargs={"type": "taken", "status": "nieuw"},
        name="dashboard",
    ),
    # maanden
    re_path(
        r"^dashboard/(?P<jaar>\d{4})/maand/(?P<maand>\d{2})/(?P<type>meldingen)/(?P<status>nieuw)/$",
        NieuweMeldingen.as_view(periode="maand"),
        kwargs={"type": "meldingen", "status": "nieuw"},
        name="dashboard",
    ),
    re_path(
        r"^dashboard/(?P<jaar>\d{4})/maand/(?P<maand>\d{2})/(?P<type>meldingen)/(?P<status>afgehandeld)/$",
        MeldingenAfgehandeld.as_view(periode="maand"),
        kwargs={"type": "meldingen", "status": "afgehandeld"},
        name="dashboard",
    ),
    re_path(
        r"^dashboard/(?P<jaar>\d{4})/maand/(?P<maand>\d{2})/(?P<type>taken)/(?P<status>aantallen)/$",
        TaaktypeAantallen.as_view(periode="maand"),
        kwargs={"type": "taken", "status": "aantallen"},
        name="dashboard",
    ),
    re_path(
        r"^dashboard/(?P<jaar>\d{4})/maand/(?P<maand>\d{2})/(?P<type>taken)/(?P<status>nieuw)/$",
        NieuweTaakopdrachten.as_view(periode="maand"),
        kwargs={"type": "taken", "status": "nieuw"},
        name="dashboard",
    ),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
]

if not settings.ENABLE_DJANGO_ADMIN_LOGIN:
    urlpatterns += [
        path(
            "admin/login/",
            RedirectView.as_view(url="/login/?next=/admin/"),
            name="admin_login",
        ),
        path(
            "admin/logout/",
            RedirectView.as_view(url="/logout/?next=/"),
            name="admin_logout",
        ),
    ]

if settings.OIDC_ENABLED:
    urlpatterns += [
        path("oidc/", include("mozilla_django_oidc.urls")),
    ]

urlpatterns += [
    path("admin/", admin.site.urls),
]

if settings.APP_ENV != "productie":
    urlpatterns += [
        path("403/", http_403, name="403"),
        path("404/", http_404, name="404"),
        path("500/", http_500, name="500"),
    ]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
