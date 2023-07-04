import stripe
from django.conf import settings
from django.db.models import Prefetch
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from qt_utils.model_loaders import (
    get_product_util_model,
    get_stripe_plan_model,
    get_stripe_price_model,
)

from .serializers import (
    CheckoutSessionResponseSerializer,
    CheckoutSessionSerializer,
    ProductIntervalSerializer,
)

stripe.api_key = settings.STRIPE_SECRET_KEY


class Products(APIView):
    def get(self, request):
        Plan = get_stripe_plan_model()
        Price = get_stripe_price_model()

        intervals = Plan.objects.values_list("interval", flat=True)

        ProductUtil = get_product_util_model()
        products = ProductUtil.objects.prefetch_related(
            "product",
            "unique_selling_points",
            Prefetch(
                "product__prices",
                queryset=Price.objects.filter(currency="usd"),
            ),
        ).all()

        combined_data = {
            "intervals": sorted(set(intervals)),
            "products": products,
        }
        response_serializer = ProductIntervalSerializer(combined_data)

        return Response(response_serializer.data, status=status.HTTP_200_OK)


class CheckoutSession(APIView):
    """
    API for creating a Stripe Checkout session
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = CheckoutSessionSerializer

    def get(self, request, price_id):
        serializer = self.serializer_class(data={"price_id": price_id})
        serializer.is_valid(raise_exception=True)

        return self.valid_request_data(request, serializer.validated_data)

    def valid_request_data(self, request, data):
        try:
            checkout_session = stripe.checkout.Session.create(
                client_reference_id=request.user.id,
                payment_method_types=["card", "paypal"],
                # customer_email = request.user.email,
                customer=request.user.customer.id,
                locale=request.LANGUAGE_CODE,
                currency="usd",
                line_items=[{"price": data["price_id"], "quantity": 1}],
                mode="subscription",
                success_url=settings.WWW_URL
                + "/platform/billing/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=settings.WWW_URL + "/platform/billing",
            )
            response_serializer = CheckoutSessionResponseSerializer(checkout_session)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as err:
            raise err
