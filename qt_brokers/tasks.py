from celery import shared_task
from qt.celery import app
import websocket
import datetime
import time
import redis
from redis.lock import Lock
import json

from django.conf import settings
from django.db import transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from qt_brokers.models import BrokerAccount, Holding

import logging


DIFFERENCE_FOR_TASK_RESTART_SECONDS = 30
RECONNECT_ATTEMPTS = 3
RECONNECT_DELAY_SECONDS = 15

# 1. Make sure that we can subscribe to all US stocks over websockets
# 2. Polling mechanism for Euronext & Toronto stocks
# 3.


# This file contains a whole lot a logging statements.
# This is really helpfull for local development as well as
# catching errors live.
logger = logging.getLogger(__name__)


@shared_task(bind=True, name='manage_stock_suffix_subscriptions')
def manage_stock_suffix_subscriptions(self):
    logger.info("Manage stock suffixes: STARTING")
    r = redis.StrictRedis.from_url(settings.REDIS_URL, decode_responses=True)

    # Retrieve the latest list of unique stock suffixes
    new_unique_stock_suffixes = set(Holding.get_all_unique_stock_suffices())
    new_unique_stock_suffixes.add("AAPL")  # Add AAPL for testing

    current_stock_suffixes = r.smembers(settings.REDIS_KEY_CURRENT_STOCK_SUFFIXES)

    removed_stock_suffixes = current_stock_suffixes - new_unique_stock_suffixes
    added_stock_suffixes = new_unique_stock_suffixes - current_stock_suffixes

    for suffix in added_stock_suffixes:
        r.sadd(settings.REDIS_KEY_CURRENT_STOCK_SUFFIXES, suffix)

    for suffix in removed_stock_suffixes:
        r.srem(settings.REDIS_KEY_CURRENT_STOCK_SUFFIXES, suffix)
    logger.info("Manage stock suffixes: FINISHED")


def add_or_remove_stock_suffixes(current_stock_suffixes, new_stock_suffices, add_callback, remove_callback):
    logger.info("ADD/REMOVE stock suffixes: START")
    removed_stock_suffixes = current_stock_suffixes - new_stock_suffices
    added_stock_suffixes = new_stock_suffices - current_stock_suffixes

    for suffix in added_stock_suffixes:
        add_callback(suffix)

    for suffix in removed_stock_suffixes:
        remove_callback(suffix)

    logger.info(f"ADD/REMOVE stock suffixes: FINISHED: {new_stock_suffices}")
    return new_stock_suffices


def attempt_reconnect(ws):
    logger.info("Finnhub WS receiver: RECONNECT")
    for i in range(RECONNECT_ATTEMPTS):
        time.sleep(RECONNECT_DELAY_SECONDS)
        try:
            ws.run_forever()
            return
        except Exception as e:
            logger.error(f"Finnhub WS receiver reconnect: ATTEMPT {i + 1}/{RECONNECT_ATTEMPTS}. Error: {e}")
    logger.error("Finnhub WS receiver reconnect: FAILED")


@shared_task(bind=True, name='finnhub_websocket_receiver')
def finnhub_websocket_receiver(self):
    logger.info("Finnhub WS receiver: STARTING")

    r = redis.StrictRedis.from_url(settings.REDIS_URL, decode_responses=True)
    lock = Lock(r, settings.REDIS_KEY_FINNHUB_WEBSOCKET_RECEIVER_LOCK)

    if not lock.acquire(blocking=False):
        logger.info("Finnhub WS receiver: PROCESS ALREADY RUNNING")
        return

    r.set(settings.REDIS_KEY_FINNHUB_WEBSOCKET_RECEIVER_TASK_ID, self.request.id)


    try:
        current_stock_suffixes = r.smembers(settings.REDIS_KEY_CURRENT_STOCK_SUFFIXES)

        def on_error(ws, error):
            logger.warning("Finnhub WS receiver: ERROR")
            logger.warning(error)

        def on_close(ws, arg1, arg2):
            logger.error("Finnhub WS receiver: CLOSE")
            logger.error(arg1)
            logger.error(arg2)
            attempt_reconnect(ws)

        def on_message(ws, message):
            logger.info("Finnhub WS receiver: MESSAGE")
            response = json.loads(message)
            logger.info(response)

            # Update the heartbeat timestamp in Redis
            r.set(settings.REDIS_KEY_FINNHUB_WEBSOCKET_RECEIVER_HEARTBEAT, datetime.datetime.utcnow().timestamp())

            if response.get("type") == "ping":
                # Update stock suffixes in Redis Cache
                logger.info("Finnhub WS receiver: REFRESH STOCK SUFFIXES")
                nonlocal current_stock_suffixes
                current_stock_suffixes = add_or_remove_stock_suffixes(current_stock_suffixes, r.smembers(settings.REDIS_KEY_CURRENT_STOCK_SUFFIXES), _ws_add_callback, _ws_remove_callback)
                logger.info(f"Finnhub WS receiver: REFRESH STOCK SUFFIXES {current_stock_suffixes}")
                return

            if not response.get("data"):
                return

            for message in response.get("data"):
                ticker = message['s']
                price = message["p"]

                r.set(ticker, price)

                # Publish a message to notify of the update
                channel_name = f"stock_update:{ticker}"
                r.publish(channel_name, price)

        def on_open(ws):
            logger.info("Finnhub WS receiver: OPEN")
            add_or_remove_stock_suffixes(set(),  current_stock_suffixes, _ws_add_callback, _ws_remove_callback)

        # For WebSocket management
        def _ws_add_callback(suffix):
            ws.send(f'{{"type": "subscribe", "symbol": "{suffix}"}}')

        def _ws_remove_callback(suffix):
            ws.send(f'{{"type": "unsubscribe", "symbol": "{suffix}"}}')

        ws = websocket.WebSocketApp(
            f"wss://ws.finnhub.io?token={settings.FINNHUB_API_KEY}",
            on_open=on_open,
            on_error=on_error,
            on_close=on_close,
            on_message=on_message,
        )

        logger.info("Finnhub WS receiver: CONNECTING")
        ws.run_forever()
    finally:
        lock.release()
        logger.error("Finnhub WS receiver: CLOSED")


@shared_task(bind=True, name='finnhub_websocket_distributor')
def finnhub_websocket_distributor(self):
    logger.info("Finnhub WS distributor: STARTING")

    r = redis.StrictRedis.from_url(settings.REDIS_URL, decode_responses=True)
    r.set(settings.REDIS_KEY_FINNHUB_WEBSOCKET_DISTRIBUTOR_TASK_ID, self.request.id)

    REFRESH_INTERVAL = 120  # refresh every 2 minutes, almost equal to the PING interval of the receiver
    last_refresh_time = time.time()

    # For pubsub management
    def _pubsub_add_callback(suffix):
        pubsub.subscribe(f'stock_update:{suffix}')

    def _pubsub_remove_callback(suffix):
        pubsub.unsubscribe(f'stock_update:{suffix}')

    try:
        pubsub = r.pubsub()

        current_stock_suffixes = r.smembers(settings.REDIS_KEY_CURRENT_STOCK_SUFFIXES)
        current_stock_suffixes = add_or_remove_stock_suffixes(set(),  current_stock_suffixes, _pubsub_add_callback, _pubsub_remove_callback)

        logger.info("Finnhub WS distributor: SUBSCRIBED")

        for message in pubsub.listen():
            logger.info("Finnhub WS distributor: MESSAGE")

            if (time.time() - last_refresh_time) > REFRESH_INTERVAL:
                logger.info("Finnhub WS distributor: REFRESH STOCK SUFFIXES")
                current_stock_suffixes = add_or_remove_stock_suffixes(current_stock_suffixes, r.smembers(settings.REDIS_KEY_CURRENT_STOCK_SUFFIXES), _pubsub_add_callback, _pubsub_remove_callback)

            # Update the heartbeat timestamp in Redis
            r.set(settings.REDIS_KEY_FINNHUB_WEBSOCKET_DISTRIBUTOR_HEARTBEAT, datetime.datetime.utcnow().timestamp())

            if message['type'] == 'message':
                logger.info("Finnhub WS distributor: DISTRIBUTE")
                # Extract stock symbol from the channel name
                stock_symbol = message['channel'].split(':')[-1]
                price = message['data']
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    group=stock_symbol,
                    message={
                        "type": "stock_price_update",
                        "stock": stock_symbol,
                        "price": price
                    }
                )
    finally:
        logger.error("Finnhub WS distributor: CLOSED")


@shared_task(bind=True, name='check_finnhub_websocket_receiver')
def check_finnhub_websocket_receiver_and_distributor(self):
    logger.info("Finnhub WS receiver & dsitributor check: STARTING")
    r = redis.StrictRedis.from_url(settings.REDIS_URL, decode_responses=True)

    last_receiver_heartbeat = datetime.datetime.utcfromtimestamp(float(r.get(settings.REDIS_KEY_FINNHUB_WEBSOCKET_RECEIVER_HEARTBEAT)))
    last_distributor_heartbeat = datetime.datetime.utcfromtimestamp(float(r.get(settings.REDIS_KEY_FINNHUB_WEBSOCKET_DISTRIBUTOR_HEARTBEAT)))
    current_time = datetime.datetime.now()

    receiver_difference = current_time - last_receiver_heartbeat
    distributor_difference = current_time - last_distributor_heartbeat

    if receiver_difference > datetime.timedelta(seconds=DIFFERENCE_FOR_TASK_RESTART_SECONDS):
        task_id = r.get(settings.REDIS_KEY_FINNHUB_WEBSOCKET_RECEIVER_TASK_ID)
        app.control.revoke(task_id, terminate=True, signal='SIGTERM')
        logger.warning(f"Revoked finnhub_websocket_receiver with task ID: {task_id}")
        r.delete(settings.REDIS_KEY_FINNHUB_WEBSOCKET_RECEIVER_HEARTBEAT)
        finnhub_websocket_receiver.delay()

    if distributor_difference > datetime.timedelta(seconds=DIFFERENCE_FOR_TASK_RESTART_SECONDS):
        task_id = r.get(settings.REDIS_KEY_FINNHUB_WEBSOCKET_DISTRIBUTOR_TASK_ID)
        app.control.revoke(task_id, terminate=True, signal='SIGTERM')
        logger.warning(f"Revoked finnhub_websocket_distributor with task ID: {task_id}")
        r.delete(settings.REDIS_KEY_FINNHUB_WEBSOCKET_DISTRIBUTOR_HEARTBEAT)
        finnhub_websocket_distributor.delay()

    logger.info("Finnhub WS receiver & dsitributor check: FINISHED")


@shared_task
def broker_account_set_holdings(broker_account_id):
    broker_account = BrokerAccount.objects.get(pk=broker_account_id)

    with transaction.atomic():
        broker_account.set_holdings_from_broker()

    broker_account.close_broker_connection()


# @shared_task
# def broker_account_update_holdings(broker_account_id):
#     broker_account = BrokerAccount.objects.get(pk=broker_account_id)

#     with transaction.atomic():
#         broker_account.set_holdings_from_broker()

#     broker_account.close_broker_connection()
