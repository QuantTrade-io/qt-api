from rest_framework import serializers

from qt_utils.serializer_fields import ImageField

from .serializer_fields import CurrentField
from .validators import device_id_exists, refresh_token_exists


class GetDeviceSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(
        validators=[refresh_token_exists],
        required=True,
    )


class DeviceSerializer(serializers.Serializer):
    id = serializers.CharField()
    token = serializers.CharField()
    image = ImageField()
    info = serializers.CharField()
    city = serializers.CharField()
    country = serializers.CharField()
    current = CurrentField()
    active = serializers.BooleanField()
    last_used = serializers.DateTimeField(source="updated_at")


class DeleteDeviceItemSerializer(serializers.Serializer):
    device_id = serializers.IntegerField(
        validators=[device_id_exists],
        required=True,
    )
