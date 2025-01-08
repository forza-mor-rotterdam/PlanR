import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object


SESSION_TIMEOUT_KEY = "_session_init_timestamp_"
SESSION_CURRENT_TIMEOUT_KEY = "_session_current_timestamp_"


class SessionTimeoutMiddleware(MiddlewareMixin):
    def close_session(self, request):
        request.session_refreshed = "delete"
        request.session.flush()
        logout(request)
        redirect_url = getattr(settings, "SESSION_TIMEOUT_REDIRECT", None)
        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect_to_login(next=request.path)

    def process_response(self, request, response):
        expire_seconds = getattr(settings, "SESSION_EXPIRE_SECONDS", False)
        expire_grace_period = getattr(
            settings, "SESSION_EXPIRE_AFTER_LAST_ACTIVITY_GRACE_PERIOD", False
        )
        max_session_seconds = getattr(
            settings, "SESSION_EXPIRE_MAXIMUM_SECONDS", settings.SESSION_COOKIE_AGE
        )
        time_now = time.time()
        init_time = request.session.get(SESSION_TIMEOUT_KEY, time_now)
        current_time = request.session.get(SESSION_CURRENT_TIMEOUT_KEY, time_now)
        session_refreshed = getattr(request, "session_refreshed", False)

        SESSION_EXPIRY_MAX_TIMESTAMP_COOKIE_NAME = getattr(
            settings,
            "SESSION_EXPIRY_MAX_TIMESTAMP_COOKIE_NAME",
            "session_expiry_max_timestamp",
        )
        SESSION_EXPIRY_TIMESTAMP_COOKIE_NAME = getattr(
            settings, "SESSION_EXPIRY_TIMESTAMP_COOKIE_NAME", "session_expiry_timestamp"
        )

        if session_refreshed == "init":
            response.set_cookie(
                SESSION_EXPIRY_MAX_TIMESTAMP_COOKIE_NAME,
                value=init_time + max_session_seconds,
                max_age=max_session_seconds,
                expires=init_time + max_session_seconds,
                domain=None,
                secure=not settings.DEBUG,
                httponly=False,
            )
            request.session_refreshed = False
        if session_refreshed in ["init", "prolong"]:
            response.set_cookie(
                SESSION_EXPIRY_TIMESTAMP_COOKIE_NAME,
                value=current_time + expire_seconds + expire_grace_period,
                max_age=max_session_seconds,
                expires=current_time,
                domain=None,
                secure=not settings.DEBUG,
                httponly=False,
            )
        if session_refreshed == "delete":
            response.delete_cookie(SESSION_EXPIRY_MAX_TIMESTAMP_COOKIE_NAME)
            response.delete_cookie(SESSION_EXPIRY_TIMESTAMP_COOKIE_NAME)
        return response

    def process_request(self, request):
        if (
            not hasattr(request, "session")
            or request.session.is_empty()
            or not request.user.is_authenticated
        ):
            return

        time_now = time.time()
        request.session_refreshed = False
        if not request.session.get(SESSION_TIMEOUT_KEY):
            request.session_refreshed = "init"
        init_time = request.session.setdefault(SESSION_TIMEOUT_KEY, time_now)
        current_time = request.session.setdefault(SESSION_CURRENT_TIMEOUT_KEY, time_now)

        expire_seconds = getattr(settings, "SESSION_EXPIRE_SECONDS", False)
        max_session_seconds = getattr(
            settings, "SESSION_EXPIRE_MAXIMUM_SECONDS", settings.SESSION_COOKIE_AGE
        )

        session_is_expired = expire_seconds and time_now - current_time > expire_seconds
        maximum_session_is_expired = time_now - init_time > max_session_seconds

        if maximum_session_is_expired:
            return self.close_session(request)
        elif session_is_expired:
            expire_grace_period = getattr(
                settings, "SESSION_EXPIRE_AFTER_LAST_ACTIVITY_GRACE_PERIOD", False
            )

            if (
                expire_grace_period
                and time_now < current_time + expire_seconds + expire_grace_period
            ):
                notification_period = getattr(
                    settings, "SESSION_EXPIRY_NOTIFICATION_PERIOD", False
                )
                if (
                    notification_period
                    and time_now - current_time
                    > expire_seconds + expire_grace_period - notification_period
                ):
                    import math

                    prolong_seconds = expire_grace_period + expire_seconds
                    if prolong_seconds > int(max_session_seconds) - int(
                        time_now - init_time
                    ):
                        prolong_seconds = int(max_session_seconds) - int(
                            time_now - init_time
                        )
                    messages.info(
                        request,
                        f"Je login is verlengd met {math.floor((prolong_seconds) / 60)} minuten",
                    )
                request.session_refreshed = "prolong"
                request.session[SESSION_CURRENT_TIMEOUT_KEY] = time_now
                return

            return self.close_session(request)
