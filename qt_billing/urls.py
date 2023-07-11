from django.urls import path

from .views import BillingPortalSession, CheckoutSession, Products

# import webhooks.py inorder to register the webhooks
from .webhooks import *  # noqa

billing_urlpatterns = [
    path("products/", Products.as_view(), name="products"),
    path(
        "checkout-session/<str:price_id>/",
        CheckoutSession.as_view(),
        name="checkout-session",
    ),
    path("portal/", BillingPortalSession.as_view(), name="portal"),
]
