from apps.regie.views import (
    detail,
    http_404,
    http_500,
    informatie_toevoegen,
    melding_afhandelen,
    melding_lijst,
    melding_pdf_download,
    meldingen_bestand,
    overview,
    root,
    taak_afronden,
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
    path("api-token-auth/", views.obtain_auth_token),
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
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("admin/", admin.site.urls),
    path("melding/", melding_lijst, name="melding_lijst"),
    path("health/", include("health_check.urls")),
    path("part/melding/", overview, name="overview"),
    path(
        "part/melding/<uuid:id>/afhandelen/",
        melding_afhandelen,
        name="melding_afhandelen",
    ),
    path(
        "part/melding/<uuid:id>/taakstarten/",
        taak_starten,
        name="taak_starten",
    ),
    path(
        "part/melding/<uuid:melding_uuid>/taak-afronden/<uuid:taakopdracht_uuid>/",
        taak_afronden,
        name="taak_afronden",
    ),
    path(
        "part/melding/<uuid:id>/informatie-toevoegen/",
        informatie_toevoegen,
        name="informatie_toevoegen",
    ),
    path("melding/<uuid:id>", detail, name="detail"),
    path(
        "download/melding/<uuid:id>/pdf/",
        melding_pdf_download,
        name="melding_pdf_download",
    ),
    re_path(r"media/", meldingen_bestand, name="meldingen_bestand"),
]

if settings.DEBUG:
    urlpatterns += [
        path("404/", http_404, name="404"),
        path("500/", http_500, name="500"),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
