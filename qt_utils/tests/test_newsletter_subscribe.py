import json

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.test import APITestCase

from qt_utils.factories import NewsletterSubscriberFactory


class NewsletterSubscriberAPITests(APITestCase):
    """
    Test Newsletter Subscription API
    """

    def test_newsletter_subscribe_without_email(self):
        """
        Subscribe to the Newsletter without providing an Email
        Should return 400
        """
        url = self._get_url()

        data = {}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], _("This field is required."))

    def test_newsletter_subscribe_invalid_email(self):
        """
        Subscribe to the Newsletter without providing an Email
        Should return 400
        """
        url = self._get_url()

        data = {"email": "this_is_not_an_email_address@"}

        response = self.client.post(url, data, format="json")
        parsed_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(parsed_response["email"][0], _("Enter a valid email address."))

    def test_newsletter_subscribe_used_email(self):
        """
        Subscribe to the Newsletter with an already used Email
        Should return 400
        """
        url = self._get_url()

        newsletter_subscriber = NewsletterSubscriberFactory()
        data = {
            "email": newsletter_subscriber.email,
        }

        response = self.client.post(url, data, format="json")
        parsed_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            parsed_response["email"][0],
            _("A subscription to our newsletter with this email already exists."),
        )

    def test_newsletter_subscribe_successfull(self):
        """
        Successfully subscribe to the Newsletter
        Should return 400
        """
        url = self._get_url()

        data = {
            "email": "test@test.com",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(
            response.data["message"], _("Succesfully subscribed to the QT Newsletter")
        )

    def _get_url(self):
        return reverse("newsletter-subscribers")
