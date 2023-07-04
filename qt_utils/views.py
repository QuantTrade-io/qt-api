from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.views import APIView

from .model_loaders import get_newsletter_subscriber_model
from .responses import ApiMessageResponse
from .serializers import (
    NewsletterSubscribersItemSerializer,
    NewsletterSubscribersSerializer,
)


class NewsletterSubscribers(APIView):
    """
    API for subscribing to the QT Newsletter
    """

    serializer_class = NewsletterSubscribersSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return self.valid_request_data(serializer.validated_data)

    def valid_request_data(self, data):
        email = data.get("email")

        NewsletterSubscriber = get_newsletter_subscriber_model()

        new_newsletter_subscriber = NewsletterSubscriber.create_newsletter_subscriber(
            email=email,
        )

        with transaction.atomic():
            new_newsletter_subscriber.save()

        return ApiMessageResponse(
            _("Succesfully subscribed to the QT Newsletter"),
            status=status.HTTP_202_ACCEPTED,
        )


class NewsletterSubscribersItem(APIView):
    """
    API for unsubscribing to the QT Newsletter
    """

    def delete(self, request, uuid):
        serializer = NewsletterSubscribersItemSerializer(data={"uuid": uuid})
        serializer.is_valid(raise_exception=True)

        return self.valid_request_data(serializer.validated_data)

    def valid_request_data(self, data):
        uuid = data.get("uuid")

        NewsletterSubscriber = get_newsletter_subscriber_model()
        newsletter_subscriber = NewsletterSubscriber.get_with_uuid(uuid)

        with transaction.atomic():
            newsletter_subscriber.delete()

        return ApiMessageResponse(
            _("Succesfully unsubscribed to the QT Newsletter"),
            status=status.HTTP_202_ACCEPTED,
        )
