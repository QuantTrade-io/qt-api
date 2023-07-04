from django.db import transaction
from djstripe import webhooks
from rest_framework import status
from rest_framework.response import Response

from qt_utils.model_loaders import get_user_model


@webhooks.handler("checkout.session.completed")
def my_handler(event, **kwargs):
    User = get_user_model()
    customer_id = event.data["object"]["customer"]

    user = User.objects.get(customer__id=customer_id)
    user.cancel_old_subscriptions()
    with transaction.atomic():
        user.set_user_subscription_status()
        user.save()

    return Response(status=status.HTTP_401_UNAUTHORIZED)
