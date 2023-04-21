from django.urls import path

from .views import Plans

billing_urlpatterns = [
    path("plans/", Plans.as_view(), name="subscription"),
]
