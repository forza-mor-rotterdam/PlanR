import os

from apps.main.utils import snake_case
from django.conf import settings
from django.test import SimpleTestCase, TestCase


class TestUtils(SimpleTestCase):
    def test_snake_case(self):
        """
        text_list only when an reopens when unhappy string
        """
        string_in = "Mock data mock mock"
        string_out = "mock_data_mock_mock"

        self.assertEqual(snake_case(string_in), string_out)


class YourTestCase(TestCase):
    def test_something(self):
        # Your test logic here

        # Check if webpack-stats.json exists
        webpack_stats_file = "/app/frontend/public/build/webpack-stats.json"
        print("WEBPACK_LOADER setting:", settings.WEBPACK_LOADER)
        self.assertTrue(
            os.path.exists(webpack_stats_file), f"{webpack_stats_file} does not exist."
        )
