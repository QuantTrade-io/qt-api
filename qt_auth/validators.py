from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from qt_utils.model_loaders import get_user_model


def email_not_taken_validator(email):
    User = get_user_model()
    if User.is_email_taken(email):
        raise ValidationError(
            _("An account for the email already exists."),
        )
