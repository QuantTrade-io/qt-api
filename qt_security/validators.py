from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from qt_utils.model_loaders import get_device_model, get_outstanding_token_model


def device_id_exists(device_id):
    Device = get_device_model()
    if not Device.objects.filter(pk=device_id).exists():
        raise ValidationError(
            _("Device not found."),
        )


def refresh_token_exists(refresh_token):
    OutstandingToken = get_outstanding_token_model()
    if not OutstandingToken.objects.filter(token=refresh_token).exists():
        raise ValidationError(
            _("Token not found."),
        )
