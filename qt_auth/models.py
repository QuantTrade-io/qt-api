from datetime import datetime, timedelta
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
import jwt

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from djstripe.models import Customer
import stripe

from .managers import CustomUserManager


stripe.api_key = settings.STRIPE_SECRET_KEY


class User(AbstractUser):
    """
    Custom user model to change behaviour of the default user model
    such as validation and required fields.
    """
    username = None
    email = models.EmailField(_("email address"), unique=True)

    are_guidelines_accepted = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    STATUS_TYPE_REGISTERED = 'R'
    STATUS_TYPE_VERIFIED = 'V'
    STATUS_TYPE_SUBSCRIBED = 'S'
    STATUS_TYPE_UNSUBSCRIBED = 'U'

    STATUS_TYPES = (
        (STATUS_TYPE_REGISTERED, 'Registered'),
        (STATUS_TYPE_VERIFIED, 'Verified'),
        (STATUS_TYPE_SUBSCRIBED, 'Subscribed'),
        (STATUS_TYPE_UNSUBSCRIBED, 'Unsubscribed'),
    )

    account_status = models.CharField(
        editable=False,
        blank=False,
        null=False,
        choices=STATUS_TYPES,
        default=STATUS_TYPE_REGISTERED,
        max_length=2
    )

    customer = models.ForeignKey(
        'djstripe.Customer', null=True, blank=True, on_delete=models.SET_NULL,
        help_text=_("The user's Stripe Customer object, if it exists")
    )
    subscription = models.ForeignKey(
        'djstripe.Subscription', null=True, blank=True, on_delete=models.SET_NULL,
        help_text=_("The user's Stripe Subscription object, if it exists")
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    JWT_TOKEN_TYPE_VERIFY_EMAIL = 'VE'
    JWT_TOKEN_TYPE_CHANGE_EMAIL = 'CE'
    JWT_TOKEN_TYPE_RESET_PASSWORD = 'RP'

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def create_user(cls, email=None, password=None, first_name=None, last_name=None, are_guidelines_accepted=None):
        if not email:
            raise ValidationError(
                _("You must enter an emailaddress."),
            )

        if not password:
            raise ValidationError(
                _("You must enter a password."),
            )

        if not first_name:
            raise ValidationError(
                _("You must enter your first name."),
            )

        if not last_name:
            raise ValidationError(
                _("You must enter your last name."),
            )

        if not are_guidelines_accepted:
            raise ValidationError(
                _("You must accept the guidelines to make an account."),
            )

        new_user = cls.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            are_guidelines_accepted=are_guidelines_accepted,
        )

        return new_user

    @classmethod
    def is_email_taken(cls, email):
        try:
            cls.objects.get(email=email)
            return True
        except User.DoesNotExist:
            return False

    def create_stripe_account(self):
        # Create mew Stripe Customer for newly registerd QT user
        stripe_customer = stripe.Customer.create(
            email = self.email,
            name = self.full_name
        )
        # Sync database with newly created stripe customer
        djstripe_customer = Customer.sync_from_stripe_data(stripe_customer)
        self.customer = djstripe_customer

        return self

    def send_email_verification(self):
        email_verification_token = self._create_email_verification_token()
        self._send_email_verification_token(email_verification_token)
        return email_verification_token

    def get_jwt_token(self):
        refresh = RefreshToken.for_user(self)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}

    def generate_token(self):
        return jwt.encode({'id': self.id}, "test", algorithm="HS256")

    def _create_email_verification_token(self):
        return jwt.encode(
            {'type': self.JWT_TOKEN_TYPE_VERIFY_EMAIL,
               'email': self.email,
               'user_id': self.pk,
               'exp': datetime.utcnow() + timedelta(days=1)},
              settings.SECRET_KEY,
              algorithm=settings.JWT_ALGORITHM)

    def _create_email_verification_link(self, email_verification_token):
        return '{0}/v1/auth/email-verification?token={1}'.format(settings.WWW_URL, email_verification_token)

    def _send_email_verification_token(self, email_verification_token):
        mail_subject = _('[QT] Email verification')
        text_content = render_to_string('qt_auth/email/verify_email.txt', {
            'full_name': self.full_name,
            'email_verification_link': self._create_email_verification_link(email_verification_token)
        })

        html_content = render_to_string('qt_auth/email/verify_email.html', {
            'full_name': self.full_name,
            'email_verification_link': self._create_email_verification_link(email_verification_token)
        })

        email = EmailMultiAlternatives(
            mail_subject, text_content, to=[self.email], from_email=settings.NO_REPLY_EMAIL_ADDRESS
        )
        email.attach_alternative(html_content, 'text/html')
        email.send()
