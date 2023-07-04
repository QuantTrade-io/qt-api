from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from qt.settings_base import NAME_MAX_LENGTH, PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH

from .validators import (
    outstanding_token_exists,
    user_email_exists_validator,
    user_email_not_taken_validator,
)


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[user_email_not_taken_validator])
    password = serializers.CharField(
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
        validators=[validate_password],
    )
    first_name = serializers.CharField(max_length=NAME_MAX_LENGTH, allow_blank=False)
    last_name = serializers.CharField(max_length=NAME_MAX_LENGTH, allow_blank=False)
    are_guidelines_accepted = serializers.BooleanField()


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField(allow_blank=False)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(allow_blank=False)
    password = serializers.CharField(
        min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
    )


class LoginRefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(allow_blank=False)


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(
        allow_blank=False, validators=[outstanding_token_exists]
    )


class RequestVerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[user_email_exists_validator])


class RequestResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[user_email_exists_validator])


class VerifyResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(allow_blank=False)
    password = serializers.CharField(
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
        validators=[validate_password],
    )


class VerifyResetEmailSerializer(serializers.Serializer):
    token = serializers.CharField(allow_blank=False)
    email_old = serializers.EmailField(validators=[user_email_exists_validator])
    email_new = serializers.EmailField(validators=[user_email_not_taken_validator])
