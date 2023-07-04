import urllib

from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import status

from qt_auth.factories import UserFactory
from qt_utils.model_loaders import (
    get_blacklisted_token_model,
    get_outstanding_token_model,
)
from qt_utils.tests.helpers import (
    get_refresh_token_for_user,
    make_authentication_headers_auth_token,
)


class DevicesAPITests(TestCase):
    """
    Test Devices API
    """

    def test_get_devices_un_auth(self):
        """
        Should return 401
        """
        url = self._get_url()

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], _("Authentication credentials were not provided.")
        )

    def test_get_devices_current_device_required(self):
        """
        Should return 400
        """
        user = UserFactory()
        url = self._get_url()

        data = {}

        header = make_authentication_headers_auth_token(user)

        response = self.client.get(url, **header, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["refresh_token"][0], _("This field is required.")
        )

    def test_get_devices_non_existing_device(self):
        """
        Should return 400
        """
        user = UserFactory()

        data = {
            "refresh_token": "non_existing_refresh_token",
        }

        url = self._get_url() + "?" + urllib.parse.urlencode(data)

        header = make_authentication_headers_auth_token(user)

        response = self.client.get(url, **header, params=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["refresh_token"][0], _("Token not found."))

    def test_get_devices_successfull(self):
        """
        Should return 200
        """
        user = UserFactory()

        # generate a couple of JWT tokens && corresponding devices
        _ = get_refresh_token_for_user(user)
        blacklist_token = get_refresh_token_for_user(user)
        token = get_refresh_token_for_user(user)

        # Blacklist one Token
        OutstandingToken = get_outstanding_token_model()
        blacklisted_token = OutstandingToken.objects.get(token=blacklist_token)
        BlacklistedToken = get_blacklisted_token_model()
        BlacklistedToken.objects.create(token=blacklisted_token)

        data = {
            "refresh_token": token,
        }

        url = self._get_url() + "?" + urllib.parse.urlencode(data)

        header = make_authentication_headers_auth_token(user)

        response = self.client.get(url, **header, params=data, format="json")

        current_count = 0
        for device in response.data:
            self.assertIn("token", device)
            self.assertIn("os", device)
            self.assertIn("family", device)
            self.assertIn("name", device)
            self.assertIn("city", device)
            self.assertIn("country", device)
            if device.get("current"):
                current_count += 1

        # # Check if exactly one device has the attribute `current` set to True.
        self.assertEqual(current_count, 1)

    def _get_url(self):
        return reverse("devices")
