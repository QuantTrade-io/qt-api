from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.test import APITestCase

from qt_auth.factories import UserFactory
from qt_utils.model_loaders import get_user_model
from qt_utils.tests.helpers import (
    get_refresh_token_for_user,
    make_authentication_headers_auth_token,
)


class UserLogoutAPITests(APITestCase):
    """
    Test User Logout API
    """

    def test_logout_without_access_token(self):
        """
        Logout user without an access token
        Should return 401
        """
        url = self._get_url()

        data = {"refresh_token": "not_a_refresh_token"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"], _("Authentication credentials were not provided.")
        )

    def test_logout_without_refresh_token(self):
        """
        Logout user without a refresh_token
        Should return 400
        """
        url = self._get_url()

        user = UserFactory()

        header = make_authentication_headers_auth_token(user)

        response = self.client.post(url, **header, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["refresh_token"][0], _("This field is required.")
        )

    def test_logout_invalid_refresh_token(self):
        """
        Logout user without a non existing/invalid refresh token
        Should return 400
        """
        url = self._get_url()

        user = UserFactory()

        header = make_authentication_headers_auth_token(user)

        data = {"refresh_token": "not_a_refresh_token"}

        response = self.client.post(url, **header, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["refresh_token"][0], _("Oustanding token not found.")
        )

    def test_logout_user_successfully(self):
        """
        Successfully logout a user && check for Blacklisting the refresh_token
        Should return 200 & other Outstanding tokens should still be valid
        """
        url = self._get_url()

        user = UserFactory()

        # Create both a header and a refresh_token, this isn't needed live!
        # This is solely for testing purposes
        refresh_token = get_refresh_token_for_user(user)
        header = make_authentication_headers_auth_token(user)

        data = {
            "refresh_token": refresh_token,
        }

        response = self.client.post(url, **header, data=data, format="json")

        User = get_user_model()
        user = User.objects.get(pk=user.id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if one token is blackisted
        self.assertEqual(user.outstandingtoken_set.count(), 2)
        self.assertEqual(
            user.outstandingtoken_set.filter(blacklistedtoken__isnull=True).count(), 1
        )

    def _get_url(self):
        return reverse("user-logout")
