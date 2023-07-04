from rest_framework import serializers

from .validators import (
    subscriber_email_not_taken_validator,
    subscriber_uuid_exists_validator,
)


class NewsletterSubscribersSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[subscriber_email_not_taken_validator])


class NewsletterSubscribersItemSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(
        validators=[subscriber_uuid_exists_validator],
        required=True,
    )
