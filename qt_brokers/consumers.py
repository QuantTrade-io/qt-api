import asyncio
import json
import websocket
import threading
import queue

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class BrokerAccountConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_queue = queue.Queue()

    @database_sync_to_async
    def _user_has_valid_subscription(self, user):
        return user.has_valid_subscription()

    @database_sync_to_async
    def _get_user_stocks(self, user):
        # Assuming you have a model structure to fetch user's stocks
        return list(user.portfolio.stocks.values_list('stock_symbol', flat=True))

    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous or not await self._user_has_valid_subscription(user):
            self.close()
            return

        await self.accept()

        # Start the thread to connect to Finnhub and get stock updates
        threading.Thread(target=self._synchronous_stock_updates).start()
        asyncio.create_task(self.send_queued_messages())

    def on_message(self, ws, message):
        self.message_queue.put(message)

    async def send_queued_messages(self):
        while True:
            message = await asyncio.to_thread(self.message_queue.get)
            if message:
                await self.send(text_data=message)

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        print("### closed ###")

    def _synchronous_stock_updates(self):
        websocket.enableTrace(True)

        def on_open(ws):
            ws.send('{"type":"subscribe","symbol":"BMW"}')

        ws = websocket.WebSocketApp(
            "wss://ws.finnhub.io?token=ciiqsbhr01qqiloeo110ciiqsbhr01qqiloeo11g",
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=on_open
        )
        ws.run_forever()

    async def disconnect(self, close_code):
        # This method will be called when the websocket is handshaken.
        # You can add some cleanup code here if needed.
        pass

    async def receive(self, text_data):
        # Handle data forwarded from on_message
        await self.send(text_data=json.loads(text_data))