from apps.dashboard.views import (
    Dashboard,
    DashboardV2,
    MeldingenAfgehandeld,
    NieuweMeldingen,
    NieuweTaakopdrachten,
    TaaktypeAantallen,
)
from apps.main.views import dashboard as dashboard_mock
from django.urls import path, re_path

urlpatterns = [
    # Dashboard
    path(
        "",
        Dashboard.as_view(),
        name="dashboard",
    ),
    path(
        "v2/",
        DashboardV2.as_view(),
        name="dashboard_v2",
    ),
    path(
        "mock/",
        dashboard_mock,
        name="dashboard_mock",
    ),
    re_path(
        r"^$",
        NieuweMeldingen.as_view(),
        kwargs={"type": "meldingen", "status": "nieuw"},
        name="dashboard",
    ),
    re_path(
        r"^(?P<jaar>\d{4})/$",
        NieuweMeldingen.as_view(periode="jaar"),
        kwargs={"type": "meldingen", "status": "nieuw"},
        name="dashboard",
    ),
    # jaren
    re_path(
        r"^(?P<jaar>\d{4})/(?P<type>meldingen)/(?P<status>nieuw)/$",
        NieuweMeldingen.as_view(periode="jaar"),
        kwargs={"type": "meldingen", "status": "nieuw"},
        name="dashboard",
    ),
    re_path(
        r"^(?P<jaar>\d{4})/(?P<type>meldingen)/(?P<status>afgehandeld)/$",
        MeldingenAfgehandeld.as_view(periode="jaar"),
        kwargs={"type": "meldingen", "status": "afgehandeld"},
        name="dashboard",
    ),
    re_path(
        r"^(?P<jaar>\d{4})/(?P<type>taken)/(?P<status>aantallen)/$",
        TaaktypeAantallen.as_view(periode="jaar"),
        kwargs={"type": "taken", "status": "aantallen"},
        name="dashboard",
    ),
    re_path(
        r"^(?P<jaar>\d{4})/(?P<type>taken)/(?P<status>nieuw)/$",
        NieuweTaakopdrachten.as_view(periode="jaar"),
        kwargs={"type": "taken", "status": "nieuw"},
        name="dashboard",
    ),
    # weken
    re_path(
        r"^(?P<jaar>\d{4})/week/(?P<week>\d{2})/(?P<type>meldingen)/(?P<status>nieuw)/$",
        NieuweMeldingen.as_view(periode="week"),
        kwargs={"type": "meldingen", "status": "nieuw"},
        name="dashboard",
    ),
    re_path(
        r"^(?P<jaar>\d{4})/week/(?P<week>\d{2})/(?P<type>meldingen)/(?P<status>afgehandeld)/$",
        MeldingenAfgehandeld.as_view(periode="week"),
        kwargs={"type": "meldingen", "status": "afgehandeld"},
        name="dashboard",
    ),
    re_path(
        r"^(?P<jaar>\d{4})/week/(?P<week>\d{2})/(?P<type>taken)/(?P<status>aantallen)/$",
        TaaktypeAantallen.as_view(periode="week"),
        kwargs={"type": "taken", "status": "aantallen"},
        name="dashboard",
    ),
    re_path(
        r"^(?P<jaar>\d{4})/week/(?P<week>\d{2})/(?P<type>taken)/(?P<status>nieuw)/$",
        NieuweTaakopdrachten.as_view(periode="week"),
        kwargs={"type": "taken", "status": "nieuw"},
        name="dashboard",
    ),
    # maanden
    re_path(
        r"^(?P<jaar>\d{4})/maand/(?P<maand>\d{2})/(?P<type>meldingen)/(?P<status>nieuw)/$",
        NieuweMeldingen.as_view(periode="maand"),
        kwargs={"type": "meldingen", "status": "nieuw"},
        name="dashboard",
    ),
    re_path(
        r"^(?P<jaar>\d{4})/maand/(?P<maand>\d{2})/(?P<type>meldingen)/(?P<status>afgehandeld)/$",
        MeldingenAfgehandeld.as_view(periode="maand"),
        kwargs={"type": "meldingen", "status": "afgehandeld"},
        name="dashboard",
    ),
    re_path(
        r"^(?P<jaar>\d{4})/maand/(?P<maand>\d{2})/(?P<type>taken)/(?P<status>aantallen)/$",
        TaaktypeAantallen.as_view(periode="maand"),
        kwargs={"type": "taken", "status": "aantallen"},
        name="dashboard",
    ),
    re_path(
        r"^(?P<jaar>\d{4})/maand/(?P<maand>\d{2})/(?P<type>taken)/(?P<status>nieuw)/$",
        NieuweTaakopdrachten.as_view(periode="maand"),
        kwargs={"type": "taken", "status": "nieuw"},
        name="dashboard",
    ),
]
