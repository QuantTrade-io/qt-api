from django.test import TestCase
from django.urls import reverse

from rest_framework.exceptions import status
from rest_framework import status


class UserLoginAPITests(TestCase):
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
        self.assertEqual(response.data["email"][0], "This field is required.")

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
        self.assertEqual(response.data["password"][0], "This field is required.")

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
        self.assertEqual(response.data["detail"], "Incorrect authentication credentials.")

    def test_login_unverified_user(self):
        """
        Login user that is not verified yet
        Should return 400
        """
        url = self._get_url()

        data = {
            "email": "test@test.com",
            "password": "test123123",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Incorrect authentication credentials.")

    def _get_url(self):
        return reverse("user-login")
