from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from qt_utils.model_loaders import get_outstanding_token_model, get_user_model


def user_email_not_taken_validator(email):
    User = get_user_model()
    if User.is_email_taken(email):
        raise ValidationError(
            _("An account for the email already exists."),
        )


def user_email_exists_validator(email):
    User = get_user_model()
    if not User.is_email_taken(email):
        raise ValidationError(_("No user found with this email."))


def outstanding_token_exists(refresh_token):
    OutstandingToken = get_outstanding_token_model()
    if not OutstandingToken.objects.filter(token=refresh_token).exists():
        raise ValidationError(
            _("Oustanding token not found."),
        )
