from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.test import APITestCase

from qt_auth.factories import UserFactory, UserUnsubscribedFactory, UserSubscribedFactory
from qt_security.factories import DeviceFactory
from qt_utils.model_loaders import (
    get_blacklisted_token_model,
    get_outstanding_token_model,
    get_user_model,
)
from qt_utils.tests.helpers import clear_stripe_customers, get_refresh_token_for_user


class UserLoginRefreshTokenAPITests(APITestCase):
    """
    Test User login using refresh token API
    All the refresh_token related stuff is tested in the library we use
    """

    def test_login_without_refresh_token(self):
        """
        Login user without providing a fresh token
        Should return 400
        """
        url = self._get_url()

        data = {}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["refresh_token"][0], _("This field is required.")
        )

    def test_login_with_invalid_refresh_token(self):
        """
        Login user with invalid refresh token
        Should return 400
        """
        url = self._get_url()

        data = {
            "refresh_token": "not_a_token",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], _("Unable to use token"))

    def test_login_refresh_token_with_no_user_found(self):
        """
        Login with an non existing used_id
        Should return 400
        """
        url = self._get_url()

        User = get_user_model()

        user = UserFactory()
        refresh_token = get_refresh_token_for_user(user)

        data = {
            "refresh_token": refresh_token,
        }

        clear_stripe_customers()
        user.delete()

        with self.assertRaises(User.DoesNotExist):
            self.client.post(url, data, format="json")

    def test_login_refresh_token_registered_account(self):
        """
        Login with refresh token registered account
        Should return 401
        """
        url = self._get_url()
        User = get_user_model()

        user = UserFactory()
        refresh_token = get_refresh_token_for_user(user)

        data = {
            "refresh_token": refresh_token,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["account_status"], User.STATUS_TYPE_REGISTERED)

    def test_login_refresh_token_change_email(self):
        """
        Login with refresh token user status change email
        Should return 401
        """
        url = self._get_url()
        User = get_user_model()

        user = UserFactory(status=User.STATUS_TYPE_CHANGE_EMAIL)
        refresh_token = get_refresh_token_for_user(user)

        data = {
            "refresh_token": refresh_token,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["account_status"], User.STATUS_TYPE_CHANGE_EMAIL)

    def test_login_refresh_token_verified_user_unsubscribed(self):
        """
        Login with refresh token verified user
        Should return 200
        """
        url = self._get_url()
        User = get_user_model()

        user = UserUnsubscribedFactory()
        token = user.get_jwt_token()

        # Ugly way of creating a Device, since it is required in the
        # LoginRefreshToken view
        OutstandingToken = get_outstanding_token_model()
        outstanding_token = OutstandingToken.objects.get(token=token["refresh"])
        DeviceFactory(user=user, token=outstanding_token)

        data = {
            "refresh_token": token["refresh"],
        }

        response = self.client.post(url, data, format="json")

        outstanding_token_updated = OutstandingToken.objects.get(token=token["refresh"])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["account_status"], User.STATUS_TYPE_VERIFIED)
        self.assertEqual(response.data["subscribed"], False)
        self.assertIn("access_token", response.data)
        self.assertNotEqual(
            outstanding_token.device.updated_at,
            outstanding_token_updated.device.updated_at,
        )

    def test_login_refresh_token_subscribed_user(self):
        """
        Login with refresh token subscribed user
        Should return 200
        """
        url = self._get_url()
        User = get_user_model()

        user = UserSubscribedFactory()
        token = user.get_jwt_token()

        # Ugly way of creating a Device, since it is required in the
        # LoginRefreshToken view
        OutstandingToken = get_outstanding_token_model()
        outstanding_token = OutstandingToken.objects.get(token=token["refresh"])
        DeviceFactory(user=user, token=outstanding_token)

        data = {
            "refresh_token": token["refresh"],
        }

        response = self.client.post(url, data, format="json")

        outstanding_token_updated = OutstandingToken.objects.get(token=token["refresh"])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["account_status"], User.STATUS_TYPE_VERIFIED
        )
        self.assertEqual(response.data["subscribed"], True)
        self.assertIn("access_token", response.data)
        self.assertNotEqual(
            outstanding_token.device.updated_at,
            outstanding_token_updated.device.updated_at,
        )

    def test_login_refresh_token_blacklisted_token(self):
        """
        Login with refresh token that is being blacklisted
        Should return 403
        """
        url = self._get_url()
        User = get_user_model()

        user = UserFactory(status=User.STATUS_TYPE_VERIFIED)
        # refresh_token = get_refresh_token_for_user(user)
        token = user.get_jwt_token()

        # Ugly way of creating a Device, since it is required in the
        # LoginRefreshToken view
        OutstandingToken = get_outstanding_token_model()
        outstanding_token = OutstandingToken.objects.get(token=token["refresh"])
        DeviceFactory(user=user, token=outstanding_token)

        outstanding_token = OutstandingToken.objects.get(token=token["refresh"])
        BlacklistedToken = get_blacklisted_token_model()
        BlacklistedToken.objects.create(token=outstanding_token)

        data = {
            "refresh_token": token["refresh"],
        }

        response = self.client.post(url, data, format="json")

        outstanding_token_updated = OutstandingToken.objects.get(token=token["refresh"])

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], _("Unable to use token"))
        self.assertEqual(
            outstanding_token.device.updated_at,
            outstanding_token_updated.device.updated_at,
        )

    def _get_url(self):
        return reverse("refresh-token")
