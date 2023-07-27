from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from qt_utils.model_loaders import get_outstanding_token_model, get_session_model


def session_id_exists(session_id):
    Session = get_session_model()
    if not Session.objects.filter(pk=session_id).exists():
        raise ValidationError(
            _("Session not found."),
        )


def refresh_token_exists(refresh_token):
    OutstandingToken = get_outstanding_token_model()
    if not OutstandingToken.objects.filter(token=refresh_token).exists():
        raise ValidationError(
            _("Token not found."),
        )
