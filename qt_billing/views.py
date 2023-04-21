from django.contrib.auth import authenticate
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from djstripe.models import Customer, Plan, Product, Price, Subscription, Plan, PaymentMethod
from qt_auth.models import User
from django.conf import settings
import stripe
import djstripe

stripe.api_key = settings.STRIPE_SECRET_KEY


class Plans(APIView):
    def get(self, request):
        plans = Plan.objects.select_related("product").all()

        import pdb; pdb.set_trace()
        return Response(status=status.HTTP_200_OK)

# class Subscription(APIView):
#
#     def post(self, request):
#         # Get this plan based on the request info
#         plan = Plan.objects.get(pk=2)
#         # Get the user based on the request info
#         user = User.objects.get(pk=1)
#
#         # Get the corrosponding Customer for the User
#         # customer, created = Customer.objects.get_or_create(email=user.email)
#
#         test = stripe.Customer.retrieve(user.customer.id)
#
#         payment_method = stripe.PaymentMethod.create(
#             type="card",
#             card={
#                 "number": "4242424242424242",
#                 "exp_month": 8,
#                 "exp_year": 2024,
#                 "cvc": "314",
#             },
#         )
#
#         stripe.PaymentMethod.attach(
#             payment_method["id"],
#             customer=user.customer,
#         )
#
#         PaymentMethod.sync_from_stripe_data(payment_method)
#         # Customer.sync_from_stripe_data(test)
#
#         stripe.Customer.modify(
#             test["id"],
#             invoice_settings={
#                 'default_payment_method': payment_method["id"],
#             },
#             # metadata={"invoice_settings.default_payment_method": "6735"},
#         )
#
#         # create subscription
#         subscription = stripe.Subscription.create(
#             customer=user.customer,
#             items=[
#                 {
#                 'plan': plan.id,
#                 },
#             ],
#             expand=['latest_invoice.payment_intent'],
#         )
#         # djstripe_subscription = Subscription.sync_from_stripe_data(subscription)
#         djstripe_subscription = djstripe.models.Subscription.sync_from_stripe_data(subscription)
#
#         # associate customer and subscription with the user
#         user.subscription = djstripe_subscription
#         user.save()
#
#         # Create a payment method for the user
#         # customer = stripe.Customer.create(
#         #     payment_method=payment_method,
#         #     email=request_user.email,
#         #     invoice_settings={
#         #         'default_payment_method': payment_method,
#         #     },
#         # )
#         # djstripe_customer = djstripe.models.Customer.sync_from_stripe_data(customer)
#
#
#         # customer.subscribe(items=[{"plan": plan}])
#
#         return Response(status=status.HTTP_200_OK)
