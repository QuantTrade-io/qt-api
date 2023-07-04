from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.test import APITestCase

from qt_auth.factories import UserFactory
from qt_utils.model_loaders import get_user_model


class RequestEmailVerificationAPITests(APITestCase):
    """
    Test reqeust email verification API
    """

    def test_request_without_email_provided(self):
        """
        Request email verification without an email provided
        Should return 400
        """
        url = self._get_url()

        data = {}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], _("This field is required."))

    def test_request_unknown_email(self):
        """
        Request email verification with an unknown email
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
        """
        Request email verification with an invalid email
        Should return 400
        """
        url = self._get_url()

        data = {
            "email": "foo_bar",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], _("No user found with this email."))

    def test_request_as_verified_user(self):
        """
        Request email verification as verified user
        Should return 405
        """
        User = get_user_model()
        user = UserFactory(status=User.STATUS_TYPE_VERIFIED)

        url = self._get_url()

        data = {
            "email": user.email,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            response.data["message"],
            _("Your email is already verified, you should be able to login."),
        )

    def test_request_as_change_email_user(self):
        """
        Request email verification as change email user successfully
        Should return 200
        """
        User = get_user_model()
        user = UserFactory(status=User.STATUS_TYPE_CHANGE_EMAIL)

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
                A new email is send to you,
                please check the instructions in order to proceed.
                """
            ),
        )

    def test_request_as_registered_user(self):
        """
        Request email verification as registered user successfully
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
                A new email is send to you,
                please check the instructions in order to proceed.
                """
            ),
        )

    def _get_url(self):
        return reverse("request-verify-email")
