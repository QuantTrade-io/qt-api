from rest_framework import serializers

from .serializer_fields import CurrentField, ImageField
from .validators import device_id_exists, refresh_token_exists


class GetDeviceSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(
        validators=[refresh_token_exists],
        required=True,
    )


class DevicesSerializer(serializers.Serializer):
    id = serializers.CharField()
    token = serializers.CharField()
    image = ImageField()
    info = serializers.CharField()
    city = serializers.CharField()
    country = serializers.CharField()
    current = CurrentField()


class DeleteDeviceItemSerializer(serializers.Serializer):
    device_id = serializers.IntegerField(
        validators=[device_id_exists],
        required=True,
    )
