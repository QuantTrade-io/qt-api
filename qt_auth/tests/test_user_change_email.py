from datetime import datetime, timedelta

from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.test import APITestCase

from qt_auth.factories import UserFactory
from qt_utils.model_loaders import get_user_model
from qt_utils.tests.helpers import (
    generate_jwt_token,
    get_refresh_token_for_user,
    make_authentication_headers_auth_token,
)


class RequestEmailResetAPITests(APITestCase):
    """
    Test request email reset API
    """

    def test_request_without_permission(self):
        """
        Request password reset without permission
        Should return 401
        """
        url = self._get_url()

        data = {}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], _("Authentication credentials were not provided.")
        )

    def test_request_successfull(self):
        """
        Request password reset successfully
        Should return 200
        """
        url = self._get_url()

        user = UserFactory()

        header = make_authentication_headers_auth_token(user)

        response = self.client.post(url, **header, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["message"],
            _(
                """
                Change emailaddress succesfully requested,
                please check your current email in order to proceed.
                """
            ),
        )

    def _get_url(self):
        return reverse("reset-email")


class VerifyEmailResetAPITests(APITestCase):
    """
    Test verify email reset API
    """

    def test_verify_with_nothing_provided(self):
        """
        Verify email reset without anything provided
        Should return 400
        """
        url = self._get_url()

        data = {}

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["token"][0], _("This field is required."))
        self.assertEqual(response.data["email_old"][0], _("This field is required."))
        self.assertEqual(response.data["email_new"][0], _("This field is required."))

    def test_verify_with_unkown_email_old(self):
        """
        Verify email reset with an unknown old email
        Should return 400
        """
        url = self._get_url()

        data = {
            "token": "not_a_token",
            "email_old": "warn_buffet@investing.com",
            "email_new": "warren_buffet@investing.com",
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["email_old"][0], _("No user found with this email.")
        )

    def test_verify_with_existing_email_new(self):
        """
        Verify email reset with an unknown old email
        Should return 400
        """
        url = self._get_url()

        user_old = UserFactory()
        user_new = UserFactory()

        data = {
            "token": "not_a_token",
            "email_old": user_old.email,
            "email_new": user_new.email,
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["email_new"][0], _("An account for the email already exists.")
        )

    def test_verify_with_invalid_token(self):
        """
        Verify email reset with an invalid token
        Should return 400
        """
        url = self._get_url()

        user_old = UserFactory()

        data = {
            "token": "not_a_token",
            "email_old": user_old.email,
            "email_new": "warren_buffet@investing.com",
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0], _("Failed to decode token"))

    def test_verify_with_invalid_token_type(self):
        """
        Verify email reset with an invalid token
        Should return 400
        """
        url = self._get_url()

        User = get_user_model()
        user_old = UserFactory()

        token = generate_jwt_token(
            User.JWT_TOKEN_TYPE_RESET_PASSWORD,
            1,
            datetime.utcnow() + timedelta(days=1),
            settings.SECRET_KEY,
        )

        data = {
            "token": token,
            "email_old": user_old.email,
            "email_new": "warren_buffet@investing.com",
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0], _("Token type does not match"))

    def test_verify_no_user_found_for_token(self):
        """
        Verify email reset with an non existing used_id
        Should return 400
        """
        user_old = UserFactory()
        fake_id = user_old.pk + 1

        User = get_user_model()

        token = generate_jwt_token(
            User.JWT_TOKEN_TYPE_RESET_EMAIL,
            fake_id,
            datetime.utcnow() + timedelta(days=1),
            settings.SECRET_KEY,
        )

        url = self._get_url()

        data = {
            "token": token,
            "email_old": user_old.email,
            "email_new": "warren_buffet@investing.com",
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[0], _("No user found for token"))

    def test_verify_not_mathing_emails(self):
        """
        Verify email reset with non matching emails
        Should return 400
        """
        user_old = UserFactory()
        user_old_2 = UserFactory()

        User = get_user_model()

        token = generate_jwt_token(
            User.JWT_TOKEN_TYPE_RESET_EMAIL,
            user_old.pk,
            datetime.utcnow() + timedelta(days=1),
            settings.SECRET_KEY,
        )

        url = self._get_url()

        data = {
            "token": token,
            "email_old": user_old_2.email,
            "email_new": "warren_buffet@investing.com",
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["message"],
            _("Unable to match the current token with the email address provided."),
        )

    def test_verify_successfull(self):
        """
        Verify email reset sucessfully && blacklisting outstanding JWT tokens
        Should return 202
        """
        User = get_user_model()

        user_old = UserFactory(status=User.STATUS_TYPE_VERIFIED)

        token = generate_jwt_token(
            User.JWT_TOKEN_TYPE_RESET_EMAIL,
            user_old.pk,
            datetime.utcnow() + timedelta(days=1),
            settings.SECRET_KEY,
        )

        url = self._get_url()

        new_email = "warren_buffet@investing.com"

        data = {
            "token": token,
            "email_old": user_old.email,
            "email_new": new_email,
        }

        # generate a couple of JWT tokens
        get_refresh_token_for_user(user_old)
        get_refresh_token_for_user(user_old)
        get_refresh_token_for_user(user_old)

        response = self.client.put(url, data, format="json")

        user = User.get_user_with_email(new_email)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(
            response.data["message"],
            _(
                """
                Email changed successfully,
                please check your new emails inbox in order to confirm.
                """
            ),
        )
        self.assertEqual(user.email, new_email)
        self.assertEqual(user.status, User.STATUS_TYPE_CHANGE_EMAIL)
        # Checks for outstanding tokens && Blacklisted tokens
        self.assertEqual(user_old.outstandingtoken_set.count(), 3)
        self.assertEqual(
            user_old.outstandingtoken_set.filter(blacklistedtoken__isnull=True).count(),
            0,
        )
        self.assertEqual(user.outstandingtoken_set.count(), 3)
        self.assertEqual(
            user.outstandingtoken_set.filter(blacklistedtoken__isnull=True).count(), 0
        )

    def test_verify_with_same_token_twice(self):
        """
        Verify email reset with the same token twice
        Should return 400
        """
        User = get_user_model()

        user_old = UserFactory(status=User.STATUS_TYPE_VERIFIED)

        token = generate_jwt_token(
            User.JWT_TOKEN_TYPE_RESET_EMAIL,
            user_old.pk,
            datetime.utcnow() + timedelta(days=1),
            settings.SECRET_KEY,
        )

        url = self._get_url()

        new_email = "warren_buffet@investing.com"

        data = {
            "token": token,
            "email_old": user_old.email,
            "email_new": new_email,
        }

        self.client.put(url, data, format="json")

        # use the new_email as the old email, and user the old email as the new email
        # in order to fullfill the requirements of those fields and make the request
        data = {
            "token": token,
            "email_old": new_email,
            "email_new": user_old.email,
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.data[0], _("Unable to reuse token multiple times."))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _get_url(self):
        return reverse("verify-reset-email")
