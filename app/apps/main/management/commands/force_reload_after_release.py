import logging

from django.contrib.sessions.backends.cache import KEY_PREFIX
from django.core.cache import cache
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        session_keys = [key for key in cache.keys("*") if key.startswith(KEY_PREFIX)]
        for key in session_keys:
            d = cache.get(key)
            d.update({"force_reload": True})
            cache.set(key, d)
