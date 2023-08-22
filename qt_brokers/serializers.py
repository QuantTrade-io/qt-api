from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from qt_utils.serializer_fields import ImageField

from brohub.broker import AuthenticationMethods

from .models import Broker, BrokerAuthenticationMethod, BrokerAccount
from .validators import authentication_method_exists_validator, broker_account_exists_validator, broker_exists_validator


class AuthenticationMethodSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    method = serializers.CharField(max_length=128, allow_blank=False)


class BrokerSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(allow_blank=False)
    image = ImageField()
    authentication_methods = AuthenticationMethodSerializer(many=True)


class PostBrokerAccountSerializer(serializers.Serializer):
    broker_id = serializers.IntegerField(required=True, validators=[broker_exists_validator])
    authentication_method_id = serializers.IntegerField(required=True, validators=[authentication_method_exists_validator])
    email = serializers.EmailField(required=False)
    password = serializers.CharField(required=False)
    username = serializers.CharField(required=False)

    def validate(self, data):
        authentication_method_id = data.get('authentication_method_id')
        broker_id = data.get('broker_id')

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        # Check the broker and authentication method combination
        if not Broker.objects.filter(pk=broker_id, authentication_methods=authentication_method_id).exists():
            raise ValidationError(_("Combination of broker & authentication method is not valid."))

        broker_authentication_method = BrokerAuthenticationMethod.objects.get(pk=authentication_method_id)

        # Validate based on the authentication method type
        if broker_authentication_method.method == AuthenticationMethods.EMAIL_PASSWORD.value:
            if not (email and password):
                errors = {}
                if not email:
                    errors['email'] = 'This field is required.'
                if not password:
                    errors['password'] = 'This field is required.'
                raise ValidationError(errors)

        elif broker_authentication_method.method == AuthenticationMethods.USERNAME_PASSWORD.value:
            if not (username and password):
                errors = {}
                if not username:
                    errors['username'] = 'This field is required.'
                if not password:
                    errors['password'] = 'This field is required.'
                raise ValidationError(errors)
        else:
            raise ValidationError("Invalid authentication method.")
        
        return data


class PatchBrokerAccountSerializer(serializers.Serializer):
    broker_account_id = serializers.IntegerField(required=True, validators=[broker_account_exists_validator])
    authentication_method_id = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)

    def validate(self, data):
        # Extract necessary data upfront
        authentication_method_id = data.get('authentication_method_id')
        broker_account_id = data.get("broker_account_id")

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        # Fetch related objects only when necessary
        broker_account = BrokerAccount.objects.get(pk=broker_account_id)
        broker_authentication_method = BrokerAuthenticationMethod.objects.get(pk=authentication_method_id)
        
        # Default values from broker_account if missing in provided data
        username = username or broker_account.username
        email = email or broker_account.email
        password = password or broker_account.password

        # Check the broker and authentication method combination
        if not Broker.objects.filter(pk=broker_account.broker.id, authentication_methods=authentication_method_id).exists():
            raise ValidationError(_("Combination of broker & authentication method is not valid."))

        # Validate based on the authentication method type
        if broker_authentication_method.method == AuthenticationMethods.EMAIL_PASSWORD.value:
            if not (email and password):
                errors = {}
                if not email:
                    errors['email'] = 'This field is required.'
                if not password:
                    errors['password'] = 'This field is required.'
                raise ValidationError(errors)

        elif broker_authentication_method.method == AuthenticationMethods.USERNAME_PASSWORD.value:
            if not (username and password):
                errors = {}
                if not username:
                    errors['username'] = 'This field is required.'
                if not password:
                    errors['password'] = 'This field is required.'
                raise ValidationError(errors)
        else:
            raise ValidationError("Invalid authentication method.")
        
        return data
    

class GetBrokerAccountSerializer(serializers.Serializer):
    broker_account_id = serializers.IntegerField(required=True, validators=[broker_account_exists_validator])


class DeleteBrokerAccountSerializer(serializers.Serializer):
    broker_account_id = serializers.IntegerField(required=True, validators=[broker_account_exists_validator])


class BrokerAccountSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)
    authentication_method = AuthenticationMethodSerializer()
    broker = BrokerSerializer()