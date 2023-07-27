from django.urls import path

from .views import Devices, SessionItem

security_urlpatterns = [
    path("devices/", Devices.as_view(), name="devices"),
    path("sessions/<int:session_id>/", SessionItem.as_view(), name="sessions"),
]
