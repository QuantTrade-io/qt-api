import json

import boto3
import stripe
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from moto import mock_s3
from rest_framework import status
from rest_framework.test import APITestCase

from qt_auth.factories import UserFactory
from qt_utils.model_loaders import get_user_model
from qt_utils.models import QTPrivateAssets
from qt_utils.tests.helpers import clear_stripe_customers


class UserRegistrationTests(APITestCase):
    """
    User registration API tests.
    """

    def setUp(self):
        self.mocked_s3 = mock_s3()
        self.mocked_s3.start()
        self.s3 = boto3.resource("s3")
        self.s3.create_bucket(
            Bucket=QTPrivateAssets.bucket_name,
            CreateBucketConfiguration={
                "LocationConstraint": settings.AWS_DEFAULT_REGION
            },
        )

    def tearDown(self):
        clear_stripe_customers()
        self.mocked_s3.stop()

    def test_empty_request(self):
        """
        Test that an empty request for registering a new user.
        """
        url = self._get_url()

        data = {}
        response = self.client.post(url, data)

        parsed_response = json.loads(response.content)

        self.assertEqual(parsed_response["email"][0], _("This field is required."))
        self.assertEqual(parsed_response["password"][0], _("This field is required."))
        self.assertEqual(parsed_response["first_name"][0], _("This field is required."))
        self.assertEqual(parsed_response["last_name"][0], _("This field is required."))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_required(self):
        """
        Test that an emailaddress is required.
        """
        url = self._get_url()
        data = {
            "password": "SuperSecretPassword(!)",
            "first_name": "Joris",
            "last_name": "Jansen",
            "are_guidelines_accepted": True,
        }
        response = self.client.post(url, data)
        parsed_response = json.loads(response.content)
        self.assertEqual(parsed_response["email"][0], _("This field is required."))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_required(self):
        """
        Test that a password is required.
        """
        url = self._get_url()
        data = {
            "email": "warrenbuffet@gmail.com",
            "first_name": "Joris",
            "last_name": "Jansen",
            "are_guidelines_accepted": True,
        }
        response = self.client.post(url, data)
        parsed_response = json.loads(response.content)
        self.assertEqual(parsed_response["password"][0], _("This field is required."))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_to_short(self):
        """
        Test that a password is to short, 1 char.
        """
        url = self._get_url()
        data = {
            "email": "warrenbuffet@gmail.com",
            "password": "q",
            "first_name": "Warren",
            "last_name": "Buffet",
            "are_guidelines_accepted": True,
        }
        response = self.client.post(url, data)
        parsed_response = json.loads(response.content)
        self.assertEqual(
            parsed_response["password"][0],
            _("This password is too short. It must contain at least 8 characters."),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """
        Test that a password is too short, 9 char.
        """
        url = self._get_url()
        data = {
            "email": "warrenbuffet@gmail.com",
            "password": "abc123def",
            "first_name": "Warren",
            "last_name": "Buffet",
            "are_guidelines_accepted": True,
        }
        response = self.client.post(url, data)
        parsed_response = json.loads(response.content)
        self.assertEqual(
            parsed_response["password"][0],
            _("Ensure this field has at least 10 characters."),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_first_name_required(self):
        """
        Test that first name is required.
        """
        url = self._get_url()
        data = {
            "email": "warrenbuffet@gmail.com",
            "password": "SuperSecretPassword(!)",
            "last_name": "Jansen",
            "are_guidelines_accepted": True,
        }
        response = self.client.post(url, data)
        parsed_response = json.loads(response.content)
        self.assertEqual(parsed_response["first_name"][0], ("This field is required."))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_last_name_required(self):
        """
        Test that last name is required.
        """
        url = self._get_url()
        data = {
            "email": "warrenbuffet@gmail.com",
            "password": "SuperSecretPassword(!)",
            "first_name": "Joris",
            "are_guidelines_accepted": True,
        }
        response = self.client.post(url, data)
        parsed_response = json.loads(response.content)
        self.assertEqual(parsed_response["last_name"][0], _("This field is required."))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_guidelines_accepted_required(self):
        """
        Test that guidelines are provided.
        """
        url = self._get_url()
        data = {
            "email": "warrenbuffet@gmail.com",
            "password": "SuperSecretPassword(!)",
            "first_name": "Joris",
            "last_name": "Jansen",
        }
        response = self.client.post(url, data)
        parsed_response = json.loads(response.content)

        self.assertEqual(
            parsed_response[0], _("You must accept the guidelines to make an account.")
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_guidelines_not_accepted(self):
        """
        Test that guidelines must be accepted.
        """
        url = self._get_url()
        data = {
            "email": "warrenbuffet@gmail.com",
            "password": "SuperSecretPassword(!)",
            "first_name": "Joris",
            "last_name": "Jansen",
            "are_guidelines_accepted": False,
        }
        response = self.client.post(url, data)
        parsed_response = json.loads(response.content)

        self.assertEqual(
            parsed_response[0], _("You must accept the guidelines to make an account.")
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_is_taken(self):
        """
        Test an email address that's already taken.
        """
        url = self._get_url()

        first_user = UserFactory()
        second_account = {
            "email": first_user.email,
            "password": "SuperDuperSecretPassword(!)123",
            "first_name": "Warren",
            "last_name": "Buffet",
            "are_guidelines_accepted": True,
        }

        response = self.client.post(url, second_account)
        parsed_response = json.loads(response.content)
        self.assertEqual(
            parsed_response["email"][0], _("An account for the email already exists.")
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_email(self):
        """
        Test that an emailaddres must be valid.
        """
        url = self._get_url()
        data = {
            "email": "not_an_email",
            "password": "SuperSecretPassword(!)",
            "first_name": "Joris",
            "last_name": "Jansen",
            "are_guidelines_accepted": True,
        }
        response = self.client.post(url, data)
        parsed_response = json.loads(response.content)
        self.assertEqual(parsed_response["email"][0], _("Enter a valid email address."))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_register(self):
        """
        Test that a user can register and that
        a corrosponding Stripe customer is
        created with the correct credentials.
        """
        url = self._get_url()
        data = {
            "email": "warrenbuffet@gmail.com",
            "password": "SuperDuperExclusivePassword",
            "first_name": "Warren",
            "last_name": "Buffet",
            "are_guidelines_accepted": True,
        }
        response = self.client.post(url, data)
        parsed_response = json.loads(response.content)
        self.assertEqual(
            parsed_response["message"],
            _(
                """
                Account succesfully registered,
                please check your email in order to proceed.
                """
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        User = get_user_model()
        user = User.objects.get(email=data["email"])

        stripe_customer = stripe.Customer.retrieve(user.customer.id)

        self.assertEqual(stripe_customer["name"], user.full_name)
        self.assertEqual(stripe_customer["email"], user.email)
        self.assertEqual(User.STATUS_TYPE_REGISTERED, user.status)
        self.assertIsNotNone(user.customer)
        self.assertTrue(user.are_guidelines_accepted)

    def _get_url(self):
        return reverse("user-register")
