import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError


class AbstractTimeStampModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class NewsletterSubscriber(AbstractTimeStampModel):
    """
    Information about a 'user' that is Subscribed
    to the newsletter (email)
    """

    email = models.EmailField(_("email address"), unique=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        verbose_name = _("Newsletter Subscriber")
        verbose_name_plural = _("Newletter Subscribers")

    def __str__(self):
        return self.email

    @classmethod
    def create_newsletter_subscriber(cls, email):
        if not email:
            raise ValidationError(
                _("You must enter an emailaddress."),
            )

        newsletter_subscriber = cls.objects.create(
            email=email,
        )

        return newsletter_subscriber

    @classmethod
    def is_email_subscribed(cls, email):
        try:
            cls.objects.get(email=email)
            return True
        except NewsletterSubscriber.DoesNotExist:
            return False

    @classmethod
    def subscriber_with_uuid_exists(cls, uuid):
        return cls.objects.filter(uuid=uuid).exists()

    @classmethod
    def get_with_uuid(cls, uuid):
        return cls.objects.get(uuid=uuid)
