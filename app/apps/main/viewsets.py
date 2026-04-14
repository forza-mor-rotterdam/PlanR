import logging

from apps.main.models import AutomatRSettings, resolve_automatr_settings_batch
from apps.main.serializers import AutomatRSettingsSerializer
from rest_framework import viewsets
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class AutomatRSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "uuid"
    queryset = AutomatRSettings.objects.all()
    serializer_class = AutomatRSettingsSerializer
    permission_classes = ()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset) # keep pagination because automatr expects this format
        instances = page if page is not None else list(queryset)
        for inst, resolved in zip(
            instances, resolve_automatr_settings_batch(i.settings for i in instances)
        ):
            inst.settings = resolved
        serializer = self.get_serializer(instances, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.settings, = resolve_automatr_settings_batch([instance.settings])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
