from rest_framework import serializers

from qt_utils.serializer_fields import ImageField

from .serializer_fields import CurrentField, DateField
from .validators import refresh_token_exists, session_id_exists


class GetDeviceSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(
        validators=[refresh_token_exists],
        required=True,
    )


class SessionSerializer(serializers.Serializer):
    id = serializers.CharField()
    city = serializers.CharField()
    country = serializers.CharField()
    current = CurrentField()
    active = serializers.BooleanField()
    last_used = DateField(source="updated_at")
    expires_at = DateField(source="token.expires_at")


class DeviceSerializer(serializers.Serializer):
    id = serializers.CharField()
    image = ImageField()
    info = serializers.CharField()
    sessions = SessionSerializer(many=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        sessions = data['sessions']
        # Sort the sessions list based on the "current" field, where 'True' comes first.
        sessions = sorted(sessions, key=lambda x: not x['current'])
        data['sessions'] = sessions
        return data


class DeleteSessionItemSerializer(serializers.Serializer):
    session_id = serializers.IntegerField(
        validators=[session_id_exists],
        required=True,
    )
