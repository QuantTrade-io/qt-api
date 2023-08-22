"""
ASGI config for qt project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from django.urls import path

from channels.routing import ProtocolTypeRouter, URLRouter

from channels_auth_token_middlewares.middleware import SimpleJWTAuthTokenMiddleware
from qt_brokers.consumers import BrokerAccountConsumer


environment = os.environ.get("ENVIRONMENT")
if environment:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"qt.settings_{environment}")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qt.settings_local")


websocket_urlpatterns = [
    path('ws/stocks/', BrokerAccountConsumer.as_asgi()),
]


application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': SimpleJWTAuthTokenMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})
