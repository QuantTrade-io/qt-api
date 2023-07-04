from datetime import datetime, timedelta

import jwt
import stripe
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db.models import Max, Prefetch
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition
from djstripe.models import Customer
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from qt_utils.model_loaders import (
    get_blacklisted_jwt_token_model,
    get_blacklisted_token_model,
    get_outstanding_token_model,
    get_stripe_customer_model,
)

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

    STATUS_TYPE_REGISTERED = "registered"
    STATUS_TYPE_VERIFIED = "verified"
    STATUS_TYPE_STRIPE_SUBSCRIBED = "subscribed"
    STATUS_TYPE_CHANGE_EMAIL = "change_email"

    STATUS_TYPES = (
        (STATUS_TYPE_REGISTERED, "Registered"),
        (STATUS_TYPE_VERIFIED, "Verified"),
        (STATUS_TYPE_STRIPE_SUBSCRIBED, "Subscribed"),
        (STATUS_TYPE_CHANGE_EMAIL, "Change Email"),
    )

    status = FSMField(choices=STATUS_TYPES, default=STATUS_TYPE_REGISTERED)

    customer = models.ForeignKey(
        "djstripe.Customer",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text=_("The user's Stripe Customer object, if it exists"),
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    JWT_TOKEN_TYPE_VERIFY_EMAIL = "VE"
    JWT_TOKEN_TYPE_RESET_EMAIL = "RE"
    JWT_TOKEN_TYPE_RESET_PASSWORD = "RP"

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def can_login(self):
        if (
            self.status == self.STATUS_TYPE_VERIFIED
            or self.status == self.STATUS_TYPE_STRIPE_SUBSCRIBED
        ):
            return True
        return False

    @classmethod
    def create_user(
        cls,
        email=None,
        password=None,
        first_name=None,
        last_name=None,
        are_guidelines_accepted=None,
    ):
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

    @classmethod
    def get_user_for_token(cls, token, jwt_type):
        try:
            token_contents = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )

            token_user_id = token_contents["user_id"]
            token_type = token_contents["type"]

            if token_type != jwt_type:
                raise ValidationError(_("Token type does not match"))

            BlacklistedJWTToken = get_blacklisted_jwt_token_model()
            __, create = BlacklistedJWTToken.objects.get_or_create(token=token)
            if not create:
                raise ValidationError(_("Unable to reuse token multiple times."))

            user = User.objects.get(pk=token_user_id)

            return user
        except jwt.InvalidSignatureError:
            raise ValidationError(_("Invalid token signature"))
        except jwt.ExpiredSignatureError:
            raise ValidationError(_("Token expired"))
        except jwt.DecodeError:
            raise ValidationError(_("Failed to decode token"))
        except User.DoesNotExist:
            raise ValidationError(_("No user found for token"))
        except KeyError:
            raise ValidationError(_("Invalid token"))

    @classmethod
    def get_user_with_email(cls, user_email):
        return cls.objects.get(email=user_email)

    @classmethod
    def get_access_token_for_refresh_token(cls, refresh_token):
        try:
            return RefreshToken(refresh_token)
        except TokenError:
            raise PermissionDenied(_("Unable to use token"))

    @transition(
        field="status", source=STATUS_TYPE_REGISTERED, target=STATUS_TYPE_VERIFIED
    )
    def set_user_status_email_verified(self):
        self.is_email_verified = True

    @transition(
        field="status",
        source=[STATUS_TYPE_STRIPE_SUBSCRIBED],
        target=STATUS_TYPE_CHANGE_EMAIL,
    )
    def set_user_status_change_email(self):
        self.is_email_verified = False

    @transition(
        field="status",
        source=[STATUS_TYPE_CHANGE_EMAIL],
        target=STATUS_TYPE_STRIPE_SUBSCRIBED,
    )
    def set_user_status_change_email_verified(self):
        self.is_email_verified = True

    @transition(
        field="status",
        source=[STATUS_TYPE_VERIFIED, STATUS_TYPE_STRIPE_SUBSCRIBED],
        target=STATUS_TYPE_STRIPE_SUBSCRIBED,
    )
    def set_user_status_subscribed(self):
        pass

    @transition(
        field="status",
        source=[STATUS_TYPE_VERIFIED, STATUS_TYPE_STRIPE_SUBSCRIBED],
        target=STATUS_TYPE_VERIFIED,
    )
    def set_user_status_unsubscribed(self):
        pass

    def update_user_status_email_verified(self):
        if self.status == self.STATUS_TYPE_CHANGE_EMAIL:
            return self.set_user_status_change_email_verified()
        return self.set_user_status_email_verified()

    def update_stripe_customer(self):
        customer = stripe.Customer.retrieve(self.customer.id)

        Customer = get_stripe_customer_model()
        Customer.sync_from_stripe_data(customer)

    def set_user_subscription_status(self):
        self.update_stripe_customer()

        # Check if current user subscription
        if self.customer.subscription and self.customer.subscription.is_valid():
            self.set_user_status_subscribed()
        else:
            self.set_user_status_unsubscribed()
        self.save()

    def has_valid_subscription(self):
        self.update_stripe_customer()

        # Check if current subscription is payd/valid
        if self.customer.subscription or not self.customer.subscription.is_valid():
            return True
        return False

    def cancel_current_subscription(self):
        # canceld current subscription(s), though it should be one!
        if not self.customer or not self.customer.subscriptions:
            return
        for sub in self.customer.subscriptions.all():
            stripe.Subscription.cancel(sub.id)

    def cancel_old_subscriptions(self):
        if not self.customer.subscriptions.count() >= 1:
            return
        # Get the user's latest subscription
        subscription_latest = self.customer.subscriptions.aggregate(Max("created"))[
            "created__max"
        ]

        # Query all the subscriptions except for the latest created one
        subscriptions_old = (
            self.customer.subscriptions.filter(
                created__lt=subscription_latest, status="active"
            )
            .exclude(created=subscription_latest)
            .order_by("created")
        )

        # Cancel oldest subscriptions
        for subscription in subscriptions_old:
            stripe.Subscription.cancel(subscription.id)
        self.update_stripe_customer()

    def create_stripe_account(self):
        # Create new Stripe Customer for newly registerd QT user
        stripe_customer = stripe.Customer.create(email=self.email, name=self.full_name)
        # Sync database with newly created stripe customer
        djstripe_customer = Customer.sync_from_stripe_data(stripe_customer)
        self.customer = djstripe_customer

        return self

    def delete_stripe_subscription(self):
        stripe.Customer.delete(self.customer.id)

    def delete_stripe_account(self):
        stripe.Customer.delete(self.customer.id)

    def send_email_verification_mail(self):
        email_verification_token = self._create_token_for_purpose(
            self.JWT_TOKEN_TYPE_VERIFY_EMAIL
        )
        mail_subject = _("[QT] Email verification")
        text_content = render_to_string(
            "qt_auth/email/verify_email.txt",
            {
                "www_url": settings.WWW_URL,
                "full_name": self.full_name,
                "email_verification_link": self._create_email_verification_link(
                    email_verification_token
                ),
            },
        )

        html_content = render_to_string(
            "qt_auth/email/verify_email.html",
            {
                "www_url": settings.WWW_URL,
                "full_name": self.full_name,
                "email_verification_link": self._create_email_verification_link(
                    email_verification_token
                ),
            },
        )

        email = EmailMultiAlternatives(
            mail_subject,
            text_content,
            to=[self.email],
            from_email=f"QuantTrade <{settings.NO_REPLY_EMAIL_ADDRESS}>",
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    def send_request_email_verification_mail(self):
        email_verification_token = self._create_token_for_purpose(
            self.JWT_TOKEN_TYPE_VERIFY_EMAIL
        )
        mail_subject = _("[QT] New Email verification")
        text_content = render_to_string(
            "qt_auth/email/request_verify_email.txt",
            {
                "www_url": settings.WWW_URL,
                "full_name": self.full_name,
                "email_verification_link": self._create_email_verification_link(
                    email_verification_token
                ),
            },
        )

        html_content = render_to_string(
            "qt_auth/email/request_verify_email.html",
            {
                "www_url": settings.WWW_URL,
                "full_name": self.full_name,
                "email_verification_link": self._create_email_verification_link(
                    email_verification_token
                ),
            },
        )

        email = EmailMultiAlternatives(
            mail_subject,
            text_content,
            to=[self.email],
            from_email=f"QuantTrade <{settings.NO_REPLY_EMAIL_ADDRESS}>",
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    def send_password_reset_mail(self):
        password_reset_token = self._create_token_for_purpose(
            self.JWT_TOKEN_TYPE_RESET_PASSWORD
        )
        mail_subject = _("[QT] Password reset")
        text_content = render_to_string(
            "qt_auth/email/password_reset.txt",
            {
                "www_url": settings.WWW_URL,
                "full_name": self.full_name,
                "password_reset_link": self._create_password_reset_link(
                    password_reset_token
                ),
            },
        )

        html_content = render_to_string(
            "qt_auth/email/password_reset.html",
            {
                "www_url": settings.WWW_URL,
                "full_name": self.full_name,
                "password_reset_link": self._create_password_reset_link(
                    password_reset_token
                ),
            },
        )

        email = EmailMultiAlternatives(
            mail_subject,
            text_content,
            to=[self.email],
            from_email=f"QuantTrade <{settings.NO_REPLY_EMAIL_ADDRESS}>",
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    def send_email_reset_mail(self):
        email_reset_token = self._create_token_for_purpose(
            self.JWT_TOKEN_TYPE_RESET_EMAIL
        )
        mail_subject = _("[QT] Change email")
        text_content = render_to_string(
            "qt_auth/email/email_reset.txt",
            {
                "www_url": settings.WWW_URL,
                "full_name": self.full_name,
                "email_reset_link": self._create_email_reset_link(email_reset_token),
            },
        )

        html_content = render_to_string(
            "qt_auth/email/email_reset.html",
            {
                "www_url": settings.WWW_URL,
                "full_name": self.full_name,
                "email_reset_link": self._create_email_reset_link(email_reset_token),
            },
        )

        email = EmailMultiAlternatives(
            mail_subject,
            text_content,
            to=[self.email],
            from_email=f"QuantTrade <{settings.NO_REPLY_EMAIL_ADDRESS}>",
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    def send_email_reset_verification_mail(self):
        email_verification_token = self._create_token_for_purpose(
            self.JWT_TOKEN_TYPE_VERIFY_EMAIL
        )
        mail_subject = _("[QT] Change email verification")
        text_content = render_to_string(
            "qt_auth/email/verify_email_reset.txt",
            {
                "www_url": settings.WWW_URL,
                "full_name": self.full_name,
                "email_verification_link": self._create_email_verification_link(
                    email_verification_token
                ),
            },
        )

        html_content = render_to_string(
            "qt_auth/email/verify_email_reset.html",
            {
                "www_url": settings.WWW_URL,
                "full_name": self.full_name,
                "email_verification_link": self._create_email_verification_link(
                    email_verification_token
                ),
            },
        )

        email = EmailMultiAlternatives(
            mail_subject,
            text_content,
            to=[self.email],
            from_email=f"QuantTrade <{settings.NO_REPLY_EMAIL_ADDRESS}>",
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    def get_jwt_token(self):
        refresh = RefreshToken.for_user(self)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}

    def get_devices(self):
        # Only return devices which tokens aren't blacklisted
        return self.devices.filter(token__blacklistedtoken=None)

    def blacklist_all_outstanding_tokens(self):
        outstanding_tokens = self.outstandingtoken_set.filter(blacklistedtoken=None)
        BlacklistedToken = get_blacklisted_token_model()
        for token in outstanding_tokens:
            BlacklistedToken.objects.create(token=token)

    def blacklist_token(self, token):
        OutstandingToken = get_outstanding_token_model()
        outstanding_token = OutstandingToken.objects.get(token=token)
        BlacklistedToken = get_blacklisted_token_model()
        BlacklistedToken.objects.create(token=outstanding_token)

    def blacklist_token_by_device_id(self, device_id):
        device = self.devices.prefetch_related(Prefetch("token")).get(pk=device_id)
        BlacklistedToken = get_blacklisted_token_model()
        _, _ = BlacklistedToken.objects.get_or_create(token=device.token)

    def _create_token_for_purpose(self, token_type, days_till_expiry=1):
        # Create token for one of the JWT token types we support internally:
        #     JWT_TOKEN_TYPE_VERIFY_EMAIL
        #     JWT_TOKEN_TYPE_RESET_EMAIL
        #     JWT_TOKEN_TYPE_RESET_PASSWORD
        return jwt.encode(
            {
                "type": token_type,
                "user_id": self.pk,
                "exp": datetime.utcnow() + timedelta(days=days_till_expiry),
            },
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    def _create_email_verification_link(self, email_verification_token):
        return "{0}/auth/email-verification?token={1}".format(
            settings.WWW_URL, email_verification_token
        )

    def _create_password_reset_link(self, password_reset_token):
        return "{0}/auth/password-reset?token={1}".format(
            settings.WWW_URL, password_reset_token
        )

    def _create_email_reset_link(self, email_reset_token):
        return "{0}/auth/email-reset?token={1}".format(
            settings.WWW_URL, email_reset_token
        )
