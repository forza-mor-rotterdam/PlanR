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
from re import Pattern as re_Pattern

from django.contrib.auth import logout
from django.urls import reverse
from django.utils.functional import cached_property

SESSION_TIMEOUT_KEY = "_session_init_timestamp_"
SESSION_CURRENT_TIMEOUT_KEY = "_session_current_timestamp_"


class SessionTimeoutMiddleware(MiddlewareMixin):
    def close_session(self, request):
        request.session_refreshed = "delete"
        request.session.flush()
        logout(request)
        print("FLUSH")
        redirect_url = getattr(settings, "SESSION_TIMEOUT_REDIRECT", None)

        # allowed = (
        #     request.method == "GET"
        #     and request.user.is_authenticated
        #     and request.path not in self.exempt_urls
        #     and not any(pat.match(request.path) for pat in self.exempt_url_patterns)
        # )
        # next = request.path if allowed else "/"

        print("request.user.is_authenticated")
        print(request.user.is_authenticated)

        return redirect_to_login(next=request.path)
        if redirect_url:
            return redirect(redirect_url)
        else:
            return redirect_to_login(next=next)

    @cached_property
    def exempt_urls(self):
        EXEMPT_URLS = getattr(settings, "SESSION_TIMEOUT_REDIRECT_EXEMPT_URLS", [])
        exempt_urls = []
        for url in EXEMPT_URLS:
            if not isinstance(url, re_Pattern):
                exempt_urls.append(url)

        return set(
            [url if url.startswith("/") else reverse(url) for url in exempt_urls]
        )

    @cached_property
    def exempt_url_patterns(self):
        EXEMPT_URLS = getattr(settings, "SESSION_TIMEOUT_REDIRECT_EXEMPT_URLS", [])
        exempt_patterns = set()
        for url_pattern in EXEMPT_URLS:
            if isinstance(url_pattern, re_Pattern):
                exempt_patterns.add(url_pattern)
        return exempt_patterns

    def process_response(self, request, response):
        expire_seconds = getattr(settings, "SESSION_EXPIRE_SECONDS", False)
        max_session_seconds = getattr(
            settings, "SESSION_EXPIRE_MAXIMUM_SECONDS", settings.SESSION_COOKIE_AGE
        )
        time_now = time.time()
        init_time = request.session.get(SESSION_TIMEOUT_KEY, time_now)
        current_time = request.session.get(SESSION_CURRENT_TIMEOUT_KEY, time_now)
        session_refreshed = getattr(request, "session_refreshed", False)

        # if session_refreshed in ["init", "prolong"]:
        if session_refreshed == "init":
            print(f"SET COOKIES: {session_refreshed}")
            response.set_cookie(
                SESSION_TIMEOUT_KEY,
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
                SESSION_CURRENT_TIMEOUT_KEY,
                value=current_time + expire_seconds,
                max_age=max_session_seconds,
                expires=current_time,
                domain=None,
                secure=not settings.DEBUG,
                httponly=False,
            )
        if session_refreshed == "delete":
            print(f"DEL COOKIES: {session_refreshed}")

            response.delete_cookie(SESSION_TIMEOUT_KEY)
            response.delete_cookie(SESSION_CURRENT_TIMEOUT_KEY)
        return response

    def process_request(self, request):
        if (
            not hasattr(request, "session")
            or request.session.is_empty()
            or not request.user.is_authenticated
        ):
            return

        time_now = time.time()
        print(request.session.get(SESSION_TIMEOUT_KEY, "NOT EXISTING"))
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
                import math

                messages.info(
                    request,
                    f"Je login is verlengd met {math.floor((expire_grace_period + expire_seconds) / 60)} minuten",
                )
                request.session_refreshed = "prolong"
                request.session[SESSION_CURRENT_TIMEOUT_KEY] = time_now
                return

            return self.close_session(request)
        # print('request.session_refreshed = "init"')
        # request.session_refreshed = "init"
