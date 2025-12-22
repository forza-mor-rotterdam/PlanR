from apps.main.models import AutomatRSettings
from rest_framework import serializers


class AutomatRSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomatRSettings
        fields = (
            "uuid",
            "name",
            "settings",
        )
        read_only_fields = (
            "uuid",
            "name",
            "settings",
        )
