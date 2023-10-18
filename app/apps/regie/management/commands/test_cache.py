import logging

from django.core.cache import cache
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        cache.set(
            "foo",
            "bar",
            60,
        )
        cached = cache.get("foo")
        return str(cached == "bar")
