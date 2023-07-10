from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.test import APITestCase

from qt_auth.factories import UserFactory
from qt_utils.model_loaders import get_user_model
from qt_utils.tests.helpers import generate_jwt_token, get_refresh_token_for_user


class RequestPasswordResetAPITests(APITestCase):
    """
    Test request password reset API
    """

    def test_request_without_email_provided(self):
        """
        Request password reset without an email provided
        Should return 400
        """
        url = self._get_url()

        data = {}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], _("This field is required."))

    def test_request_unknown_email(self):
        """
        Request password reset with an unknown email
        Should return 400
        """
        url = self._get_url()

        data = {
            "email": "warrenbuffet@gmail.com",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], _("No user found with this email."))

    def test_request_invalid_email(self):
        """f
        Request password reset with an invalid email
        Should return 400
        """
        url = self._get_url()

        data = {
            "email": "warren@buf",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], _("No user found with this email."))

    def test_request_successfull(self):
        """
        Request password reset successfully
        Should return 200
        """
        user = UserFactory()

        url = self._get_url()

        data = {
            "email": user.email,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["message"],
            _(
                """
                Password reset email succesfully requested,
                please check your email in order to proceed.
                """
            ),
        )

    def _get_url(self):
        return reverse("reset-password")


class VerifyPasswordResetAPITests(APITestCase):
    """
    Test request password reset API
    """

    def test_verify_with_nothing_provided(self):
        """
        Verify password reset without anything provided
        Should return 400
        """
        url = self._get_url()

        data = {}

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["token"][0], _("This field is required."))
        self.assertEqual(response.data["password"][0], _("This field is required."))

    def test_verify_with_invalid_token(self):
        """
        Verify password reset with an invalid token
        Should return 400
        """
        url = self._get_url()

        data = {
            "password": "ThisWontWork123",
            "token": "not_a_token",
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0], _("Failed to decode token"))

    def test_verify_no_user_found(self):
        """
        Verify password reset with an non existing used_id
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
            "password": "ThisWontWork123",
            "token": token,
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0], _("No user found for token"))

    def test_verify_token_types_do_not_match(self):
        """
        Verify password reset with an invalid token type
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
            "password": "ThisWontWork123",
            "token": token,
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0], _("Token type does not match"))

    def test_verify_expired_token(self):
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
            "password": "ThisWontWork123",
            "token": token,
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0], _("Token expired"))

    def test_verify_invalid_token_signature(self):
        """
        Verify password reset with an invalid token signature
        Should return 400
        """
        User = get_user_model()

        token = generate_jwt_token(
            User.JWT_TOKEN_TYPE_RESET_PASSWORD,
            1,
            datetime.utcnow() - timedelta(days=1),
            "not_the_real_signing_key",
        )

        url = self._get_url()

        data = {
            "password": "ThisWontWork123",
            "token": token,
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0], _("Invalid token signature"))

    def test_verify_successfull(self):
        """
        Verify password reset sucessfully
        Should return 202
        """
        User = get_user_model()
        user = UserFactory()

        token = user._create_token_for_purpose(User.JWT_TOKEN_TYPE_RESET_PASSWORD)

        url = self._get_url()

        password = "ThisWillWork123"

        data = {
            "password": password,
            "token": token,
        }

        # generate a couple of JWT tokens
        get_refresh_token_for_user(user)
        get_refresh_token_for_user(user)
        get_refresh_token_for_user(user)

        response = self.client.put(url, data, format="json")

        # updated user
        user = User.objects.get(pk=user.id)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(
            response.data["message"],
            _(
                """
                Password changed successfully,
                you'll be logged-out across all devices within a couple of minutes.
                """
            ),
        )
        self.assertTrue(check_password(password, user.password))
        # Checks for outstanding tokens && Blacklisted tokens
        self.assertEqual(user.outstandingtoken_set.count(), 3)
        self.assertEqual(
            user.outstandingtoken_set.filter(blacklistedtoken__isnull=True).count(), 0
        )

    def test_verify_with_same_token_twice(self):
        """
        Verify password reset with the same token twice
        Should return 400
        """
        User = get_user_model()
        user = UserFactory()

        token = user._create_token_for_purpose(User.JWT_TOKEN_TYPE_RESET_PASSWORD)

        url = self._get_url()

        password = "ThisWillWork123"

        data = {
            "password": password,
            "token": token,
        }

        self.client.put(url, data, format="json")
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.data[0], _("Unable to reuse token multiple times."))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.put(url, data, format="json")

    def _get_url(self):
        return reverse("verify-reset-password")
