from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from qt_utils.model_loaders import get_newsletter_subscriber_model


def subscriber_email_not_taken_validator(email):
    NewsletterSubscriber = get_newsletter_subscriber_model()
    if NewsletterSubscriber.is_email_subscribed(email):
        raise ValidationError(
            _("A subscription to our newsletter with this email already exists."),
        )


def subscriber_uuid_exists_validator(uuid):
    NewsletterSubscriber = get_newsletter_subscriber_model()
    if not NewsletterSubscriber.subscriber_with_uuid_exists(uuid=uuid):
        raise ValidationError(
            _("No Newsletter Subscriber found with the provided information."),
        )
