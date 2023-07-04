from django.urls import path

from .views import DeviceItem, Devices

security_urlpatterns = [
    path("devices/", Devices.as_view(), name="devices"),
    path("devices/<int:device_id>/", DeviceItem.as_view(), name="device"),
]
