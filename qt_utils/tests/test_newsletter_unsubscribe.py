import uuid

from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import status

from qt_utils.factories import NewsletterSubscriberFactory


class NewsletterSubscriberItemAPITests(TestCase):
    """
    Test Newsletter Subscriber Item API
    """

    def test_newsletter_unsubscribe_invalid_uuid(self):
        """
        Unsubscribe to the Newsletter API with an invalid uuid
        Should return 400
        """
        url = self._get_url(uuid.uuid4())

        response = self.client.delete(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["uuid"][0],
            _("No Newsletter Subscriber found with the provided information."),
        )

    def test_newsletter_unsubcsription_valid_uuid(self):
        """
        Unsubscribe to the Newsletter API with an existing subscriber (uuid)
        Should return 202
        """
        newsletter_subscriber = NewsletterSubscriberFactory()
        url = self._get_url(newsletter_subscriber.uuid)

        response = self.client.delete(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(
            response.data["message"], _("Succesfully unsubscribed to the QT Newsletter")
        )

    def _get_url(self, uuid):
        return reverse("newsletter-subscribers-item", kwargs={"uuid": uuid})
