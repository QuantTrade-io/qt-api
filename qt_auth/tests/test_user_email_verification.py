import json
from datetime import datetime, timedelta

from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.test import APITestCase

from qt_auth.factories import UserFactory
from qt_utils.model_loaders import get_user_model
from qt_utils.tests.helpers import generate_jwt_token


class UserEmailVerificationAPITests(APITestCase):
    """
    Test User Email Verification API
    """

    def test_verify_email_without_token(self):
        """
        Verify email without providing a token
        Should return 400
        """
        url = self._get_url()

        data = {}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["token"][0], _("This field is required."))

    def test_verify_email_with_invalid_token(self):
        """
        Verify email with an invalid token
        Should return 400
        """
        url = self._get_url()

        data = {
            "token": "not_a_token",
        }

        response = self.client.post(url, data, format="json")
        parsed_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(parsed_response[0], _("Failed to decode token"))

    def test_verify_email_no_user_found(self):
        """
        Verify email with an non existing used_id
        Should return 400
        """
        User = get_user_model()

        token = generate_jwt_token(
            User.JWT_TOKEN_TYPE_VERIFY_EMAIL,
            1,
            datetime.utcnow() + timedelta(days=1),
            settings.SECRET_KEY,
        )

        url = self._get_url()

        data = {
            "token": token,
        }

        response = self.client.post(url, data, format="json")
        parsed_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(parsed_response[0], _("No user found for token"))

    def test_verify_email_token_types_do_not_match(self):
        """
        Verify email with an invalid token type
        Should return 400
        """
        User = get_user_model()

        token = generate_jwt_token(
            User.JWT_TOKEN_TYPE_RESET_PASSWORD,
            1,
            datetime.utcnow() + timedelta(days=1),
            settings.SECRET_KEY,
        )

        url = self._get_url()

        data = {
            "token": token,
        }

        response = self.client.post(url, data, format="json")

        parsed_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(parsed_response[0], _("Token type does not match"))

    def test_verify_email_expired_token(self):
        """
        Verify email with an expired token
        Should return 400
        """
        User = get_user_model()

        token = generate_jwt_token(
            User.JWT_TOKEN_TYPE_VERIFY_EMAIL,
            1,
            datetime.utcnow() - timedelta(days=1),
            settings.SECRET_KEY,
        )

        url = self._get_url()

        data = {
            "token": token,
        }

        response = self.client.post(url, data, format="json")
        parsed_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(parsed_response[0], _("Token expired"))

    def test_verify_email_invalid_token_signature(self):
        """
        Verify email with an invalid token signature
        Should return 400
        """
        User = get_user_model()

        token = generate_jwt_token(
            User.JWT_TOKEN_TYPE_VERIFY_EMAIL,
            1,
            datetime.utcnow() - timedelta(days=1),
            "not_the_real_signing_key",
        )

        url = self._get_url()

        data = {
            "token": token,
        }

        response = self.client.post(url, data, format="json")
        parsed_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(parsed_response[0], _("Invalid token signature"))

    def test_verify_email_invalid_user_status(self):
        """
        Verify email with an invalid User status
        Should return 405
        """
        User = get_user_model()

        user = UserFactory(status=User.STATUS_TYPE_VERIFIED)

        token = user._create_token_for_purpose(User.JWT_TOKEN_TYPE_VERIFY_EMAIL)

        url = self._get_url()

        data = {
            "token": token,
        }

        response = self.client.post(url, data, format="json")
        parsed_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            parsed_response["message"],
            _("Unable to verify email in the current status."),
        )

    def test_verify_email_successfull(self):
        """
        Verify email sucessfully
        Should return 202
        """
        User = get_user_model()
        user = UserFactory(is_email_verified=False)

        token = user._create_token_for_purpose(User.JWT_TOKEN_TYPE_VERIFY_EMAIL)

        url = self._get_url()

        data = {
            "token": token,
        }

        response = self.client.post(url, data, format="json")
        parsed_response = json.loads(response.content)

        # updated user
        user = User.objects.get(pk=user.id)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(
            parsed_response["message"],
            _("Account succesfully verified, welcome to the Team."),
        )
        self.assertEqual(user.status, User.STATUS_TYPE_VERIFIED)
        self.assertTrue(user.is_email_verified)

        response = self.client.post(url, data, format="json")

    def test_verify_change_email_successfull(self):
        """
        Verify changed email sucessfully
        Should return 202
        """
        User = get_user_model()
        user_old = UserFactory(
            is_email_verified=False, status=User.STATUS_TYPE_CHANGE_EMAIL
        )

        token = user_old._create_token_for_purpose(User.JWT_TOKEN_TYPE_VERIFY_EMAIL)

        url = self._get_url()

        data = {
            "token": token,
        }

        response = self.client.post(url, data, format="json")
        parsed_response = json.loads(response.content)

        # updated user
        user_new = User.objects.get(pk=user_old.id)

        self.assertEqual(user_old.status, User.STATUS_TYPE_CHANGE_EMAIL)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(
            parsed_response["message"],
            _("Account succesfully verified, welcome to the Team."),
        )
        self.assertEqual(user_new.status, User.STATUS_TYPE_STRIPE_SUBSCRIBED)
        self.assertTrue(user_new.is_email_verified)

    def test_verify_email_with_same_token_twice(self):
        """
        Verify email twice with the same token
        Should return 400
        """
        User = get_user_model()
        user_old = UserFactory(is_email_verified=False)

        token = user_old._create_token_for_purpose(User.JWT_TOKEN_TYPE_VERIFY_EMAIL)

        url = self._get_url()

        data = {
            "token": token,
        }

        # Same request twice
        self.client.post(url, data, format="json")
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.data[0], _("Unable to reuse token multiple times."))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _get_url(self):
        return reverse("verify-email")
