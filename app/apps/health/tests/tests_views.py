from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from health_check.db.backends import DatabaseBackend
from health_check.exceptions import ServiceUnavailable


class HealthCheckViewTest(TestCase):
    databases = {"default", "alternate"}

    def test_returns_503_on_service_unavailable(self):
        with patch.object(
            DatabaseBackend,
            "check_status",
            side_effect=ServiceUnavailable("test failure"),
        ):
            response = self.client.get(reverse("health_check_home"))
            self.assertEqual(response.status_code, 503)

    def test_happy_path_is_not_500(self):
        response = self.client.get(reverse("health_check_home"))
        self.assertNotEqual(response.status_code, 500)
