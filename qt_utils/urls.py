from django.urls import path

from .views import CheckAuthentication

utils_urlpatterns = [
    path("check-authentication/", CheckAuthentication.as_view(), name="check-authentication"),
]
