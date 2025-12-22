import logging

from apps.main.models import AutomatRSettings
from apps.main.serializers import AutomatRSettingsSerializer
from rest_framework import viewsets

logger = logging.getLogger(__name__)


class AutomatRSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "uuid"
    queryset = AutomatRSettings.objects.all()
    serializer_class = AutomatRSettingsSerializer
    permission_classes = ()
