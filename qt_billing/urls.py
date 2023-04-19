from django.urls import path

from .views import Subscription

billing_urlpatterns = [
    path("", Subscription.as_view(), name="subscription"),
]
