from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.test import APITestCase

from qt_auth.factories import UserFactory
from qt_utils.model_loaders import get_user_model
from qt_utils.tests.helpers import make_authentication_headers_auth_token


class DeviceItemAPITests(APITestCase):
    """
    Test Device Item API
    """

    def test_delete_device_item_un_auth(self):
        """
        Should return 401
        """
        url = self._get_url(1)

        response = self.client.delete(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], _("Authentication credentials were not provided.")
        )

    def test_delete_device_item_non_existing(self):
        """
        Should return 400
        """
        # ID 1 will exist, since we create a auth_header
        url = self._get_url(2)

        user = UserFactory()
        header = make_authentication_headers_auth_token(user)

        response = self.client.delete(url, **header, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["device_id"][0], _("Device not found."))

    def test_delete_device_item_successfull(self):
        """
        Should return 200
        """
        user = UserFactory()
        header = make_authentication_headers_auth_token(user)
        user_device = user.devices.first()

        url = self._get_url(user_device.id)

        response = self.client.delete(url, **header, format="json")

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(
            response.data["message"],
            _(
                """
                Device succesfully deleted form the logged in list,
                it could take a couple of minutes
                before the changes are affected on the device itself.
                """
            ),
        )

        # Try to reuse refresh token for new access_token
        User = get_user_model()

        with self.assertRaises(PermissionDenied):
            User.get_access_token_for_refresh_token(user_device.token.token)

    def _get_url(self, device_id):
        return reverse("device", kwargs={"device_id": device_id})
