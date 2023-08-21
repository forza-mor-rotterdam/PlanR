import locale
import logging
import os
import sys
from os.path import join

import requests

locale.setlocale(locale.LC_ALL, "nl_NL.UTF-8")
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRUE_VALUES = [True, "True", "true", "1"]

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY", os.getenv("SECRET_KEY", os.getenv("APP_SECRET"))
)

ENVIRONMENT = os.getenv("ENVIRONMENT")
DEBUG = ENVIRONMENT == "development"

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

USE_TZ = True
TIME_ZONE = "Europe/Amsterdam"
USE_L10N = True
USE_I18N = True
LANGUAGE_CODE = "nl-NL"
LANGUAGES = [("nl", "Dutch")]

DEFAULT_ALLOWED_HOSTS = ".forzamor.nl,localhost,127.0.0.1,.mor.local"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", DEFAULT_ALLOWED_HOSTS).split(",")

INSTALLED_APPS = (
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.gis",
    "django.contrib.postgres",
    "rest_framework",
    "rest_framework.authtoken",
    "drf_spectacular",
    "webpack_loader",
    "corsheaders",
    "mozilla_django_oidc",
    "health_check",
    "health_check.cache",
    "health_check.db",
    "health_check.contrib.migrations",
    # Apps
    "apps.health",
    "apps.rotterdam_formulier_html",
    "apps.regie",
    "apps.authenticatie",
)

MIDDLEWARE = (
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django_permissions_policy.PermissionsPolicyMiddleware",
    "csp.middleware.CSPMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "mozilla_django_oidc.middleware.SessionRefresh",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

# django-permissions-policy settings
PERMISSIONS_POLICY = {
    "accelerometer": [],
    "ambient-light-sensor": [],
    "autoplay": [],
    "camera": [],
    "display-capture": [],
    "document-domain": [],
    "encrypted-media": [],
    "fullscreen": [],
    "geolocation": [],
    "gyroscope": [],
    "interest-cohort": [],
    "magnetometer": [],
    "microphone": [],
    "midi": [],
    "payment": [],
    "usb": [],
}

STATICFILES_DIRS = (
    [
        "/app/frontend/public/build/",
    ]
    if DEBUG
    else []
)

STATIC_URL = "/static/"
STATIC_ROOT = os.path.normpath(join(os.path.dirname(BASE_DIR), "static"))

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.normpath(join(os.path.dirname(BASE_DIR), "media"))

# Database settings
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST_OVERRIDE")
DATABASE_PORT = os.getenv("DATABASE_PORT_OVERRIDE")

DEFAULT_DATABASE = {
    "ENGINE": "django.contrib.gis.db.backends.postgis",
    "NAME": DATABASE_NAME,  # noqa:
    "USER": DATABASE_USER,  # noqa
    "PASSWORD": DATABASE_PASSWORD,  # noqa
    "HOST": DATABASE_HOST,  # noqa
    "PORT": DATABASE_PORT,  # noqa
}

DATABASES = {
    "default": DEFAULT_DATABASE,
}
DATABASES.update(
    {
        "alternate": DEFAULT_DATABASE,
    }
    if ENVIRONMENT == "test"
    else {}
)
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
AUTH_USER_MODEL = "authenticatie.Gebruiker"

SITE_ID = 1
SITE_NAME = os.getenv("SITE_NAME", "Regie")
SITE_DOMAIN = os.getenv("SITE_DOMAIN", "localhost")

WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": not DEBUG,
        "POLL_INTERVAL": 0.1,
        "IGNORE": [r".+\.hot-update.js", r".+\.map"],
        "LOADER_CLASS": "webpack_loader.loader.WebpackLoader",
        "STATS_FILE": "/static/webpack-stats.json"
        if not DEBUG
        else "/app/frontend/public/build/webpack-stats.json",
    }
}
DEV_SOCKET_PORT = os.getenv("DEV_SOCKET_PORT", "9000")


# Django REST framework settings
REST_FRAMEWORK = dict(
    PAGE_SIZE=5,
    UNAUTHENTICATED_USER={},
    UNAUTHENTICATED_TOKEN={},
    DEFAULT_PAGINATION_CLASS="rest_framework.pagination.LimitOffsetPagination",
    DEFAULT_FILTER_BACKENDS=("django_filters.rest_framework.DjangoFilterBackend",),
    DEFAULT_THROTTLE_RATES={
        "nouser": os.getenv("PUBLIC_THROTTLE_RATE", "60/hour"),
    },
    DEFAULT_PARSER_CLASSES=[
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    DEFAULT_SCHEMA_CLASS="drf_spectacular.openapi.AutoSchema",
    DEFAULT_VERSIONING_CLASS="rest_framework.versioning.NamespaceVersioning",
    DEFAULT_PERMISSION_CLASSES=("rest_framework.permissions.IsAuthenticated",),
    DEFAULT_AUTHENTICATION_CLASSES=(
        "rest_framework.authentication.TokenAuthentication",
    ),
)


# Django security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = "strict-origin"
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "SAMEORIGIN"
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_PRELOAD = True
CORS_ORIGIN_WHITELIST = ()
CORS_ORIGIN_ALLOW_ALL = False
USE_X_FORWARDED_HOST = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_NAME = "__Secure-sessionid" if not DEBUG else "sessionid"
CSRF_COOKIE_NAME = "__Secure-csrftoken" if not DEBUG else "csrftoken"
SESSION_COOKIE_SAMESITE = "Lax" # Strict does not work well together with OIDC
CSRF_COOKIE_SAMESITE = "Lax" # Strict does not work well together with OIDC

# Settings for Content-Security-Policy header
CSP_DEFAULT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'self'",)
CSP_FRAME_SRC = (
    "'self'",
    "iam.forzamor.nl",
)
CSP_SCRIPT_SRC = (
    ("'self'", "'unsafe-eval'", "unpkg.com")
    if not DEBUG
    else ("'self'", "'unsafe-eval'", "unpkg.com", "'unsafe-inline'")
)
CSP_IMG_SRC = [
    "'self'",
    "blob:",
    "data:",
    "unpkg.com",
    "tile.openstreetmap.org",
    "placehold.it",
    "www.placeholder.com",
    "via.placeholder.com",
    "mor-core-acc.forzamor.nl",
]

CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "data:", "unpkg.com")
CSP_CONNECT_SRC = ("'self'",) if not DEBUG else ("'self'", "ws:")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.messages.context_processors.messages",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "config.context_processors.general_settings",
            ],
        },
    }
]

REDIS_URL = "redis://redis:6379"
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
        },
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT", 25)
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "0") in TRUE_VALUES
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "0") in TRUE_VALUES
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "no-reply@forzamor.nl")

MELDINGEN_URL = os.getenv("MELDINGEN_URL", "https://mor-core-acc.forzamor.nl")
MELDINGEN_API_URL = os.getenv("MELDINGEN_API_URL", f"{MELDINGEN_URL}/api/v1")
MELDINGEN_API_HEALTH_CHECK_URL = os.getenv(
    "MELDINGEN_API_HEALTH_CHECK_URL", f"{MELDINGEN_URL}/health/"
)
MELDINGEN_TOKEN_API = os.getenv(
    "MELDINGEN_TOKEN_API", f"{MELDINGEN_URL}/api-token-auth/"
)
MELDINGEN_TOKEN_TIMEOUT = 60 * 5
MELDINGEN_USERNAME = os.getenv("MELDINGEN_USERNAME")
MELDINGEN_PASSWORD = os.getenv("MELDINGEN_PASSWORD")

MELDING_AANMAKEN_URL = os.getenv(
    "MELDING_AANMAKEN_URL",
    "https://serviceformulier-acc.benc.forzamor.nl/melding/aanmaken",
)

LOG_LEVEL = "DEBUG" if DEBUG else "INFO"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "verbose",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "/app/uwsgi.log",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        "celery": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
    },
}

OIDC_RP_CLIENT_ID = os.getenv("OIDC_RP_CLIENT_ID")
OIDC_RP_CLIENT_SECRET = os.getenv("OIDC_RP_CLIENT_SECRET")
OIDC_VERIFY_SSL = os.getenv("OIDC_VERIFY_SSL", True) in TRUE_VALUES
OIDC_USE_NONCE = os.getenv("OIDC_USE_NONCE", True) in TRUE_VALUES

OIDC_REALM = os.getenv("OIDC_REALM")
AUTH_BASE_URL = os.getenv("AUTH_BASE_URL")
OPENID_CONFIG_URI = os.getenv(
    "OPENID_CONFIG_URI",
    f"{AUTH_BASE_URL}/realms{OIDC_REALM}/.well-known/openid-configuration",
)
OPENID_CONFIG = {}
try:
    OPENID_CONFIG = requests.get(OPENID_CONFIG_URI).json()
except requests.exceptions.ConnectionError as e:
    logger.error(f"OPENID_CONFIG FOUT, url: {OPENID_CONFIG_URI}, error: {e}")

OIDC_OP_AUTHORIZATION_ENDPOINT = os.getenv(
    "OIDC_OP_AUTHORIZATION_ENDPOINT", OPENID_CONFIG.get("authorization_endpoint")
)
OIDC_OP_TOKEN_ENDPOINT = os.getenv(
    "OIDC_OP_TOKEN_ENDPOINT", OPENID_CONFIG.get("token_endpoint")
)
OIDC_OP_USER_ENDPOINT = os.getenv(
    "OIDC_OP_USER_ENDPOINT", OPENID_CONFIG.get("userinfo_endpoint")
)
OIDC_OP_JWKS_ENDPOINT = os.getenv(
    "OIDC_OP_JWKS_ENDPOINT", OPENID_CONFIG.get("jwks_uri")
)
CHECK_SESSION_IFRAME = os.getenv(
    "CHECK_SESSION_IFRAME", OPENID_CONFIG.get("check_session_iframe")
)
OIDC_RP_SCOPES = os.getenv(
    "OIDC_RP_SCOPES",
    " ".join(OPENID_CONFIG.get("scopes_supported", ["openid", "email", "profile"])),
)
OIDC_OP_LOGOUT_ENDPOINT = os.getenv(
    "OIDC_OP_LOGOUT_ENDPOINT",
    OPENID_CONFIG.get("end_session_endpoint"),
)

if OIDC_OP_JWKS_ENDPOINT:
    OIDC_RP_SIGN_ALGO = "RS256"

AUTHENTICATION_BACKENDS = [
    "apps.authenticatie.auth.OIDCAuthenticationBackend",
    "django.contrib.auth.backends.ModelBackend",
]
OIDC_OP_LOGOUT_URL_METHOD = "apps.authenticatie.views.provider_logout"
ALLOW_LOGOUT_GET_METHOD = True
OIDC_STORE_ID_TOKEN = True
OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS = int(
    os.getenv("OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS", "300")
)

LOGIN_REDIRECT_URL = "/"
LOGIN_REDIRECT_URL_FAILURE = "/"
LOGOUT_REDIRECT_URL = OIDC_OP_LOGOUT_ENDPOINT
LOGIN_URL = "/oidc/authenticate/"
