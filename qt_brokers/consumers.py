import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class BrokerAccountConsumer(AsyncJsonWebsocketConsumer):
    @database_sync_to_async
    def _user_has_valid_subscription(self):
        return self.user.has_valid_subscription()
    
    @database_sync_to_async
    def _get_unique_ticker_suffixes(self):
        return list(self.user.get_unique_ticker_suffixes())

    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous or not await self._user_has_valid_subscription():
            self.close()
            return

        self.stock_suffixes = await self._get_unique_ticker_suffixes()

        for stock_suffix in self.stock_suffixes:
            print("I AM HERE")
            print(stock_suffix)
            await self.channel_layer.group_add(
                stock_suffix,
                self.channel_name
            )

        await self.channel_layer.group_add(
            "AAPL",
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        for stock_suffix in self.stock_suffixes:
            await self.channel_layer.group_discard(
                stock_suffix,
                self.channel_name
            )

    async def stock_price_update(self, event):
        # This will be triggered when an update for a stock is received
        await self.send(text_data=json.dumps({
            'stock': event['stock'],
            'price': event['price']
        }))
