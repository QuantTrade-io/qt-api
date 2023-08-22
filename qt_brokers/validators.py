from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from .models import Broker, BrokerAuthenticationMethod, BrokerAccount

def authentication_method_exists_validator(authentication_method_id):
    if not BrokerAuthenticationMethod.objects.filter(pk=authentication_method_id).exists():
        raise ValidationError(
            _("Authentication method not found."),
        )

def broker_exists_validator(broker_id):
    if not Broker.objects.filter(pk=broker_id).exists():
        raise ValidationError(
            _("Broker not found."),
        )

def broker_account_exists_validator(broker_account_id):
    if not BrokerAccount.objects.filter(pk=broker_account_id).exists():
        raise ValidationError(
            _("Broker Account not found."),
        )