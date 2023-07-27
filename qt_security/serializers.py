from rest_framework import serializers

from qt_utils.serializer_fields import ImageField

from .serializer_fields import CurrentField
from .validators import refresh_token_exists, session_id_exists


class GetDeviceSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(
        validators=[refresh_token_exists],
        required=True,
    )


class SessionSerializer(serializers.Serializer):
    id = serializers.CharField()
    token = serializers.CharField()
    city = serializers.CharField()
    country = serializers.CharField()
    current = CurrentField()
    active = serializers.BooleanField()
    last_used = serializers.DateTimeField(source="updated_at")


class DeviceSerializer(serializers.Serializer):
    id = serializers.CharField()
    image = ImageField()
    info = serializers.CharField()
    sessions = SessionSerializer(many=True)


class DeleteSessionItemSerializer(serializers.Serializer):
    session_id = serializers.IntegerField(
        validators=[session_id_exists],
        required=True,
    )
