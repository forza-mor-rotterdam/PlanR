from apps.authenticatie.views import GebruikerProfielView, SessionTimerView
from apps.health.views import healthz
from apps.main.views import (
    LichtmastView,
    LoginView,
    LogoutView,
    MeldingDetail,
    ModalContentView,
    TakenAanmakenStreamView,
    TakenAanmakenView,
    gebruiker_info,
    http_403,
    http_404,
    http_500,
    informatie_toevoegen,
    locatie_aanpassen,
    melding_aanmaken,
    melding_afhandelen,
    melding_annuleren,
    melding_heropenen,
    melding_hervatten,
    melding_lijst,
    melding_next,
    melding_pauzeren,
    melding_pdf_download,
    melding_spoed_veranderen,
    melding_verzonden,
    meldingen_bestand,
    publiceer_topic,
    root,
    sidesheet_actueel,
    taak_afronden,
    taak_annuleren,
)
from apps.release_notes.views import (
    ReleaseNoteDetailView,
    ReleaseNoteListViewPublic,
    SnackOverzichtStreamView,
    SnackOverzichtView,
    SnackView,
    ToastView,
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
    path("modal-content/", ModalContentView.as_view(), name="modal_content"),
    path("session-timer/", SessionTimerView.as_view(), name="session_timer"),
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
    path("melding/<uuid:id>/", MeldingDetail.as_view(), name="melding_detail"),
    path("lichtmast/<int:lichtmast_id>/", LichtmastView.as_view(), name="lichtmast"),
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
        "melding/<uuid:id>/taken-aanmaken/",
        TakenAanmakenView.as_view(),
        name="taken_aanmaken",
    ),
    path(
        "melding/<uuid:id>/taken-aanmaken/stream/",
        TakenAanmakenStreamView.as_view(),
        name="taken_aanmaken_stream",
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
    # Notificaties
    path(
        "notificaties/snack/",
        SnackView.as_view(),
        name="snack_lijst",
    ),
    path(
        "notificaties/toast/",
        ToastView.as_view(),
        name="toast_lijst",
    ),
    path(
        "notificaties/snack/overzicht/",
        SnackOverzichtView.as_view(),
        name="snack_overzicht",
    ),
    path(
        "notificaties/snack/overzicht/stream/",
        SnackOverzichtStreamView.as_view(),
        name="snack_overzicht_stream",
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
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("beheer/", include("apps.beheer.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
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
