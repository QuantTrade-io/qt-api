from django.contrib.auth.hashers import check_password
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.test import APITestCase

from qt_auth.factories import UserSubscribedFactory, UserUnsubscribedFactory
from qt_utils.model_loaders import get_user_model
from qt_utils.tests.helpers import make_authentication_headers_auth_token


class AuthenticatedUserSettingsAPITests(APITestCase):
    """
    Test Authenticated User Settings API
    """

    def test_patch_authenticated_user_settings_without_subscription(self):
        """
        Should return 401
        """
        user = UserUnsubscribedFactory()
        header = make_authentication_headers_auth_token(user)

        url = self._get_url()

        response = self.client.patch(url, **header, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            _("Your account is not associated with a valid subscription."),
        )

    def test_patch_authenticated_user_settings_with_subscription_without_passwords(
        self,
    ):
        """
        Should return 400
        """
        user = UserSubscribedFactory()
        header = make_authentication_headers_auth_token(user)

        url = self._get_url()

        data = {}

        response = self.client.patch(url, **header, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["password_old"][0], _("This field is required."))
        self.assertEqual(response.data["password_new"][0], _("This field is required."))

    def test_patch_authenticated_user_settings_with_subscription_invalid_password_old(
        self,
    ):
        """
        Should return 400
        """
        user = UserSubscribedFactory()
        header = make_authentication_headers_auth_token(user)

        url = self._get_url()

        data = {
            "password_old": "dehdenknieneh",
            "password_new": "menvattezetochniebarend",
        }

        response = self.client.patch(url, **header, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], _("Password is not valid"))

    def test_patch_authenticated_user_settings_with_subscription_successfull(self):
        """
        Should return 202
        """
        User = get_user_model()
        user = UserSubscribedFactory()
        header = make_authentication_headers_auth_token(user)

        url = self._get_url()

        password_new = "menvattezetochniebarend"

        data = {"password_old": "AhhYeahWakeupYeah", "password_new": password_new}

        response = self.client.patch(url, **header, data=data, format="json")

        # updated user
        user = User.objects.get(pk=user.id)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(check_password(password_new, user.password))
        self.assertEqual(
            response.data["message"],
            _(
                """
                Password changed successfully,
                you'll be logged-out across all devices within a couple of minutes.
                """
            ),
        )

    def _get_url(self):
        return reverse("authenticated-user-settings")
