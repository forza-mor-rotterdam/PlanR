import time

from django.conf import settings
from django.contrib import messages
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
        request.session.flush()
        redirect_url = getattr(settings, "SESSION_TIMEOUT_REDIRECT", None)
        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect_to_login(next=request.path)

    def process_request(self, request):
        if not hasattr(request, "session") or request.session.is_empty():
            return

        time_now = time.time()

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
                import math

                print("VERLENG SESSION")
                messages.info(
                    request,
                    f"Je login is verlengd met {math.floor((expire_grace_period + expire_seconds) / 60)} minuten",
                )
                request.session[SESSION_CURRENT_TIMEOUT_KEY] = time_now
                return
            return self.close_session(request)
