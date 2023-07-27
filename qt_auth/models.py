from datetime import datetime, timedelta

import boto3
import jwt
import stripe
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db.models import Max, Q
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMField, transition
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from qt_security.checkers import validate_image_size_and_mime_type
from qt_utils.helpers import aws_instance_directory_path, get_s3_image
from qt_utils.model_loaders import (
    get_blacklisted_jwt_token_model,
    get_blacklisted_token_model,
    get_outstanding_token_model,
    get_stripe_customer_model,
)
from qt_utils.models import QTPrivateAssets, QTPublicAssets

from .managers import CustomUserManager

DEFAULT_PROFILE_IMAGE_KEY = "images/unkown_user.png"

s3_resource = boto3.resource(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)
stripe.api_key = settings.STRIPE_SECRET_KEY


class User(AbstractUser):
    """
    Custom user model to change behaviour of the default user model
    such as validation and required fields.
    """

    username = None
    email = models.EmailField(_("email address"), unique=True)

    image = models.ImageField(
        upload_to=aws_instance_directory_path,
        blank=True,
        null=True,
        storage=QTPrivateAssets(),
        max_length=250,
    )

    are_guidelines_accepted = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    STATUS_TYPE_REGISTERED = "registered"
    STATUS_TYPE_VERIFIED = "verified"
    STATUS_TYPE_CHANGE_EMAIL = "change_email"

    STATUS_TYPES = (
        (STATUS_TYPE_REGISTERED, "Registered"),
        (STATUS_TYPE_VERIFIED, "Verified"),
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
    def billing_portal(self):
        return stripe.billing_portal.Session.create(
            customer=self.customer.id,
            return_url=f"{settings.WWW_URL}/platform/account/settings",
        )

    @property
    def get_image(self):
        if self.image and self.image.url:
            return self.image.url

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

        image = get_s3_image(QTPublicAssets.bucket_name, DEFAULT_PROFILE_IMAGE_KEY)

        new_user = cls.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            are_guidelines_accepted=are_guidelines_accepted,
            image=image,
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

    def update(self, first_name=None, last_name=None, image=None):
        if first_name is not None:
            self.first_name = first_name

        if last_name is not None:
            self.last_name = last_name

        if image is not None:
            validate_image_size_and_mime_type(image)
            self.image = image

        return self

    def update_password(self, password_new):
        self.set_password(password_new)
        self.blacklist_all_outstanding_tokens()

        return self

    @transition(
        field="status",
        source=[STATUS_TYPE_REGISTERED, STATUS_TYPE_CHANGE_EMAIL],
        target=STATUS_TYPE_VERIFIED,
    )
    def set_user_status_email_verified(self):
        self.is_email_verified = True

    @transition(
        field="status", source=STATUS_TYPE_VERIFIED, target=STATUS_TYPE_CHANGE_EMAIL
    )
    def set_user_status_change_email(self):
        self.is_email_verified = False

    def has_valid_subscription(self):
        # Check if current subscription is payd/valid
        if self.customer.subscription and self.customer.subscription.is_valid():
            return True
        return False

    def delete_aws_resources_for_user(self):
        bucket = s3_resource.Bucket(QTPrivateAssets.bucket_name)
        for obj in bucket.objects.filter(Prefix=f"user_{self.email}/"):
            s3_resource.Object(QTPrivateAssets.bucket_name, obj.key).delete()

    def cancel_current_subscription(self):
        # cancel current subscription(s), though it should be one!
        try:
            if not self.customer or not self.customer.subscriptions.exists():
                return
            for subscription in self.customer.subscriptions.all():
                subscription.cancel()
        except get_stripe_customer_model().DoesNotExist:
            return

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
            subscription.cancel()

    def create_stripe_account(self):
        # Create new Stripe Customer for newly registerd QT user.
        # Can't be done via dj-stripe.
        stripe_customer = stripe.Customer.create(email=self.email, name=self.full_name)

        # Sync database with newly created stripe customer
        Customer = get_stripe_customer_model()
        djstripe_customer = Customer.sync_from_stripe_data(stripe_customer)
        self.customer = djstripe_customer

        return self

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

    def get_current_devices_and_session(self):
        return (
            self.devices.prefetch_related(
                "sessions__token", "sessions__token__blacklistedtoken"
            )
            .annotate(latest_session_update=Max("sessions__updated_at"))
            .filter(
                Q(sessions__token__blacklistedtoken__isnull=True)
                | Q(
                    sessions__token__blacklistedtoken__isnull=False,
                    sessions__updated_at__gte=timezone.now()
                    - timezone.timedelta(days=5),
                )
            )
            .distinct()
        )

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
        return "{0}/auth/verify-email?token={1}".format(
            settings.WWW_URL, email_verification_token
        )

    def _create_password_reset_link(self, password_reset_token):
        return "{0}/auth/verify-password?token={1}".format(
            settings.WWW_URL, password_reset_token
        )

    def _create_email_reset_link(self, email_reset_token):
        return "{0}/auth/reset-email?token={1}".format(
            settings.WWW_URL, email_reset_token
        )
