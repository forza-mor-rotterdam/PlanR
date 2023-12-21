import json
import logging

import jwt
import requests
from django.conf import settings
from django.core.validators import URLValidator

logger = logging.getLogger(__name__)


class MercureService:
    _subscribe_targets = ["*"]
    _publish_targets = []
    _mercure_url = None
    _mercure_publisher_jwt_key = None
    _mercure_subscriber_jwt_key = None

    class ConfigException(Exception):
        ...

    def __init__(self):
        self._publish_targets = settings.MERCURE_PUBLISH_TARGETS
        try:
            validate = URLValidator()
            validate(settings.APP_MERCURE_PUBLIC_URL)
        except Exception as e:
            logentry = (
                f"Config error: APP_MERCURE_PUBLIC_URL is not a valid url, error: {e}"
            )
            logger.warning(logentry)
            raise MercureService.ConfigException(logentry)
        if not settings.MERCURE_PUBLISHER_JWT_KEY:
            logentry = "Config error: MERCURE_PUBLISHER_JWT_KEY is None"
            logger.warning(logentry)
            raise MercureService.ConfigException(logentry)
        if not settings.MERCURE_SUBSCRIBER_JWT_KEY:
            logentry = "Config error: MERCURE_SUBSCRIBER_JWT_KEY is None"
            logger.warning(logentry)
            raise MercureService.ConfigException(logentry)

        logger.info(f"Public url: {settings.APP_MERCURE_PUBLIC_URL}")
        logger.info(f"Internal url: {settings.APP_MERCURE_INTERNAL_URL}")
        self._mercure_url = settings.APP_MERCURE_INTERNAL_URL
        logger.info(f"_mercure_url: {self._mercure_url}")
        self._mercure_publisher_jwt_key = settings.MERCURE_PUBLISHER_JWT_KEY
        self._mercure_subscriber_jwt_key = settings.MERCURE_SUBSCRIBER_JWT_KEY

    def _get_headers(self):
        token = self._get_jwt_token(
            self._mercure_publisher_jwt_key, {"publisher": "server"}
        )
        logger.info(f"Auth token token: {token}")
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def _get_jwt_token(self, key, mercure_payload=None):
        payload = {
            "mercure": {
                "subscribe": self._subscribe_targets,
                "publish": self._publish_targets,
            },
        }
        if mercure_payload:
            payload["mercure"]["payload"] = mercure_payload
        return jwt.encode(
            payload,
            key,
            algorithm="HS256",
        )

    def publish(self, topic: str, data: dict = {}):
        logger.info(f"Publish with topic: {topic}")
        logger.info(f"Publish with data: {data}")

        data = {
            "topic": topic,
            "data": json.dumps(data),
        }

        response = requests.post(
            self._mercure_url,
            data=data,
            headers=self._get_headers(),
        )
        response.raise_for_status()
        logger.info(f"Publish response status_code: {response.status_code}")
        logger.info(f"Publish response text: {response.text}")

        return response

    def get_subscriptions(self):
        response = requests.get(
            f"{self._mercure_url}/subscriptions",
            headers=self._get_headers(),
        )
        logger.info(f"Subscriptions response status_code: {response.status_code}")
        logger.info(f"Subscriptions response text: {response.text}")
        response.raise_for_status()
        return response.json()

    def get_subscriber_token(self, payload=dict):
        return self._get_jwt_token(self._mercure_subscriber_jwt_key, payload)