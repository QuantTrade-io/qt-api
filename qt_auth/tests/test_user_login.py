from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.test import APITestCase

from qt_auth.factories import UserFactory
from qt_utils.model_loaders import get_user_model


class UserLoginAPITests(APITestCase):
    """
    Test User Login API
    """

    def test_login_without_email(self):
        """
        Login user without an emailaddress
        Should return 400
        """
        url = self._get_url()

        data = {
            "password": "test123123",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], _("This field is required."))

    def test_login_without_password(self):
        """
        Login user without a password
        Should return 400
        """
        url = self._get_url()

        data = {
            "email": "test@test.com",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["password"][0], _("This field is required."))

    def test_login_non_existing_user(self):
        """
        Login user without a non existing user
        Should return 401
        """
        url = self._get_url()

        data = {
            "email": "test@test.com",
            "password": "test123123",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], _("Incorrect authentication credentials.")
        )

    def test_login_unverified_user(self):
        """
        Unsuccessfull login a user that is registered but not verified
        Should return 401 & registered user status
        """
        user = UserFactory(is_email_verified=True)

        url = self._get_url()

        data = {
            "email": user.email,
            "password": "AhhYeahWakeupYeah",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["account_status"], get_user_model().STATUS_TYPE_REGISTERED
        )
        self.assertNotIn("token", response.data)

    def test_login_verified_user(self):
        """
        Succesfull login a user that is verified
        Should return 200, verified user status & token
        """
        User = get_user_model()
        user = UserFactory(is_email_verified=True, status=User.STATUS_TYPE_VERIFIED)

        url = self._get_url()

        data = {
            "email": user.email,
            "password": "AhhYeahWakeupYeah",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["account_status"], User.STATUS_TYPE_VERIFIED)
        self.assertIn("token", response.data)
        self.assertIn("refresh", response.data["token"])
        self.assertIn("access", response.data["token"])

    def test_login_subscribed_user(self):
        """
        Succesfull login a user that has a subscription
        Should return 200 & subscribed user status & token
        """
        User = get_user_model()
        user = UserFactory(
            is_email_verified=True, status=User.STATUS_TYPE_STRIPE_SUBSCRIBED
        )

        url = self._get_url()

        data = {
            "email": user.email,
            "password": "AhhYeahWakeupYeah",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["account_status"], User.STATUS_TYPE_STRIPE_SUBSCRIBED
        )
        self.assertIn("token", response.data)
        self.assertIn("refresh", response.data["token"])
        self.assertIn("access", response.data["token"])

    def _get_url(self):
        return reverse("user-login")
