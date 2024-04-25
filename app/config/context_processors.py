import logging

from apps.release_notes.models import ReleaseNote
from apps.services.mercure import MercureService
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from utils.diversen import absolute

logger = logging.getLogger(__name__)


def general_settings(context):
    user = getattr(context, "user", None)

    gebruiker = (
        user.serialized_instance() if hasattr(user, "serialized_instance") else {}
    )
    unwatched_count = 0
    if user and getattr(user, "is_authenticated", False):
        unwatched_count = ReleaseNote.count_unwatched(user)

    template_basis = getattr(user, "profiel.context.template", None) if user else None

    session_expiry_max_timestamp = context.session.get("_session_init_timestamp_", 0)
    if session_expiry_max_timestamp:
        session_expiry_max_timestamp += settings.SESSION_EXPIRE_MAXIMUM_SECONDS
    session_expiry_timestamp = context.session.get("_session_current_timestamp_", 0)
    if session_expiry_timestamp:
        session_expiry_timestamp += settings.SESSION_EXPIRE_SECONDS

    mercure_service = None
    subscriber_token = None
    try:
        mercure_service = MercureService()
    except MercureService.ConfigException:
        ...

    if mercure_service:
        payload = {
            "gebruiker": gebruiker,
            "timestamp": int(timezone.now().timestamp()),
        }
        subscriber_token = mercure_service.get_subscriber_token(payload)

    deploy_date_formatted = None
    if settings.DEPLOY_DATE:
        deploy_date = timezone.datetime.strptime(
            settings.DEPLOY_DATE, "%d-%m-%Y-%H-%M-%S"
        )
        deploy_date_formatted = deploy_date.strftime("%d-%m-%Y %H:%M:%S")

    return {
        "MELDINGEN_URL": settings.MELDINGEN_URL,
        "DEBUG": settings.DEBUG,
        "DEV_SOCKET_PORT": settings.DEV_SOCKET_PORT,
        "GET": context.GET,
        "ABSOLUTE_ROOT": absolute(context).get("ABSOLUTE_ROOT"),
        "SESSION_EXPIRY_MAX_TIMESTAMP": session_expiry_max_timestamp,
        "SESSION_EXPIRY_TIMESTAMP": session_expiry_timestamp,
        "LOGOUT_URL": reverse("oidc_logout"),
        "LOGIN_URL": f"{reverse('oidc_authentication_init')}?next={absolute(context).get('FULL_URL')}",
        "TEMPLATE_BASIS": template_basis,
        "ENVIRONMENT": settings.ENVIRONMENT,
        "APP_MERCURE_PUBLIC_URL": settings.APP_MERCURE_PUBLIC_URL,
        "MERCURE_SUBSCRIBER_TOKEN": subscriber_token,
        "GEBRUIKER": gebruiker,
        "GIT_SHA": settings.GIT_SHA,
        "UNWATCHED_COUNT": unwatched_count,
        "APP_ENV": settings.APP_ENV,
        "MOR_CORE_URL_PREFIX": settings.MOR_CORE_URL_PREFIX,
        "DEPLOY_DATE": deploy_date_formatted,
    }
