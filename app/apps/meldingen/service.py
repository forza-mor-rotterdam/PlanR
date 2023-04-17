import requests
from django.conf import settings
from django.core.cache import cache
from requests import Request, Response


class MeldingenService:
    _api_base_url = None
    _timeout: tuple[int, ...] = (5, 10)

    def __init__(self, api_base_url: str, *args, **kwargs: dict):
        self._api_base_url = api_base_url.strip().rstrip("/")
        super().__init__(*args, **kwargs)

    def get_url(self, url):
        return f"{self._api_base_url}{url}"

    def get_headers(self):
        meldingen_token = cache.get("meldingen_token")
        if not meldingen_token:
            token_response = requests.post(
                settings.MELDINGEN_TOKEN_API,
                json={
                    "username": settings.MELDINGEN_USERNAME,
                    "password": settings.MELDINGEN_PASSWORD,
                },
            )
            if token_response.status_code == 200:
                meldingen_token = token_response.json().get("token")
                cache.set(
                    "meldingen_token", meldingen_token, settings.MELDINGEN_TOKEN_TIMEOUT
                )

        headers = {"Authorization": f"Token {meldingen_token}"}
        return headers

    def do_request(self, url, method="get", data={}):

        action: Request = getattr(requests, method)
        action_params: dict = {
            "url": self.get_url(url),
            "headers": self.get_headers(),
            "json": data,
            "timeout": self._timeout,
        }
        response: Response = action(**action_params)
        return response.json()

    def get_melding_lijst(self, query_string=""):
        return self.do_request(f"/melding/?{query_string}")

    def get_melding(self, id, query_string=""):
        return self.do_request(f"/melding/{id}/?{query_string}")
