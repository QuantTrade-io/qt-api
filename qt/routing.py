from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from qt_brokers import consumers

websocket_urlpatterns = [
    path('ws/stocks/', consumers.StockConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': URLRouter(websocket_urlpatterns),
})