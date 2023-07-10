import stripe
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.test import APITestCase

from qt_auth.factories import UserSubscribedFactory, UserUnsubscribedFactory
from qt_utils.tests.helpers import make_authentication_headers_auth_token

stripe.api_key = settings.STRIPE_SECRET_KEY


class AuthenticatedUserAPITests(APITestCase):
    """
    Test Authenticated User API
    """

    def test_get_authenticated_user_without_subscription(self):
        """
        Should return 401
        """
        user = UserUnsubscribedFactory()
        header = make_authentication_headers_auth_token(user)

        url = self._get_url()

        response = self.client.get(url, **header, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            _("Your account is not associated with a valid subscription."),
        )

    def test_get_authenticated_user_with_subscription(self):
        """
        Should return 200
        """
        user = UserSubscribedFactory()
        header = make_authentication_headers_auth_token(user)

        url = self._get_url()

        response = self.client.get(url, **header, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], user.id)
        self.assertEqual(response.data["email"], user.email)
        self.assertEqual(response.data["first_name"], user.first_name)
        self.assertEqual(response.data["last_name"], user.last_name)
        self.assertEqual(response.data["image"], user.image)
        self.assertEqual(len(response.data["devices"]), 1)

        for device in response.data["devices"]:
            self.assertIn("id", device)
            self.assertIn("token", device)
            self.assertIn("image", device)
            self.assertIn("info", device)
            self.assertIn("city", device)
            self.assertIn("country", device)
            self.assertIn("current", device)

    def _get_url(self):
        return reverse("authenticated-user")