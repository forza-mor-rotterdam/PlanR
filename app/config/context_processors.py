import logging

from apps.main.services import MercureService
from apps.release_notes.models import ReleaseNote
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def general_settings(context):
    user = getattr(context, "user", None)

    gebruiker = (
        user.serialized_instance() if hasattr(user, "serialized_instance") else {}
    )
    unwatched_count = 0
    if user and getattr(user, "is_authenticated", False):
        unwatched_count = ReleaseNote.count_unwatched(user)

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
        "DEBUG": settings.DEBUG,
        "DEV_SOCKET_PORT": settings.DEV_SOCKET_PORT,
        "APP_MERCURE_PUBLIC_URL": settings.APP_MERCURE_PUBLIC_URL,
        "MERCURE_SUBSCRIBER_TOKEN": subscriber_token,
        "GEBRUIKER": gebruiker,
        "GIT_SHA": settings.GIT_SHA,
        "UNWATCHED_COUNT": unwatched_count,
        "APP_ENV": settings.APP_ENV,
        "MOR_CORE_URL_PREFIX": settings.MOR_CORE_URL_PREFIX,
        "DEPLOY_DATE": deploy_date_formatted,
        "SESSION_EXPIRE_SECONDS": settings.SESSION_EXPIRE_SECONDS,
        "SESSION_EXPIRE_AFTER_LAST_ACTIVITY_GRACE_PERIOD": settings.SESSION_EXPIRE_AFTER_LAST_ACTIVITY_GRACE_PERIOD,
        "SESSION_EXPIRY_MAX_TIMESTAMP_COOKIE_NAME": settings.SESSION_EXPIRY_MAX_TIMESTAMP_COOKIE_NAME,
        "SESSION_EXPIRY_TIMESTAMP_COOKIE_NAME": settings.SESSION_EXPIRY_TIMESTAMP_COOKIE_NAME,
        "SESSION_EXPIRY_NOTIFICATION_PERIOD": settings.SESSION_EXPIRY_NOTIFICATION_PERIOD,
        "SESSION_EXPIRY_MAX_NOTIFICATION_PERIOD": settings.SESSION_EXPIRY_MAX_NOTIFICATION_PERIOD,
    }
