import logging
from datetime import datetime, timedelta

from apps.main.constanten import BEGRAAFPLAATSEN_LOOKUP
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
        "DEBUG": settings.DEBUG,
        "DEV_SOCKET_PORT": settings.DEV_SOCKET_PORT,
        "SESSION_SHOW_TIMER_SECONDS": settings.SESSION_SHOW_TIMER_SECONDS,
        "SESSION_CHECK_INTERVAL_SECONDS": settings.SESSION_CHECK_INTERVAL_SECONDS,
        "SESSION_EXPIRY_MAX_TIMESTAMP": session_expiry_max_timestamp,
        "SESSION_EXPIRY_MAX_DATETIME": datetime.fromtimestamp(
            session_expiry_max_timestamp
        ),
        "SESSION_EXPIRY_TIMESTAMP": session_expiry_timestamp,
        "SESSION_EXPIRY_DATETIME": datetime.fromtimestamp(session_expiry_timestamp),
        "SESSION_EXPIRE_AFTER_LAST_ACTIVITY_GRACE_PERIOD": settings.SESSION_EXPIRE_AFTER_LAST_ACTIVITY_GRACE_PERIOD,
        "SESSION_EXPIRY_DATETIME_PLUS_GRACE_PERIOD": datetime.fromtimestamp(
            session_expiry_timestamp
        )
        + timedelta(seconds=settings.SESSION_EXPIRE_AFTER_LAST_ACTIVITY_GRACE_PERIOD),
        "APP_MERCURE_PUBLIC_URL": settings.APP_MERCURE_PUBLIC_URL,
        "MERCURE_SUBSCRIBER_TOKEN": subscriber_token,
        "GEBRUIKER": gebruiker,
        "GIT_SHA": settings.GIT_SHA,
        "UNWATCHED_COUNT": unwatched_count,
        "APP_ENV": settings.APP_ENV,
        "MOR_CORE_URL_PREFIX": settings.MOR_CORE_URL_PREFIX,
        "DEPLOY_DATE": deploy_date_formatted,
        "BEGRAAFPLAATSEN_LOOKUP": BEGRAAFPLAATSEN_LOOKUP,
    }
