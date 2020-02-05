from igz.packages.nats.clients import NATSClient
from igz.packages.eventbus.action import ActionWrapper
import logging
import sys
import json
from typing import Callable

from nats.aio.client import Msg as NATSMessage


class EventBus:
    _consumers = None
    _producer = None
    _logger = None

    def __init__(self, messages_storage_manager, logger=None):
        self._consumers = dict()
        self._messages_storage_manager = messages_storage_manager
        if logger is None:
            logger = logging.getLogger('event-bus')
            logger.setLevel(logging.DEBUG)
            log_handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(asctime)s: %(module)s: %(levelname)s: %(message)s')
            log_handler.setFormatter(formatter)
            logger.addHandler(log_handler)
        self._logger = logger

    def __wrap_non_dict_message(self, msg):
        return {"message": msg}

    async def rpc_request(self, topic, message, timeout=10):
        if not isinstance(message, dict):
            message = self.__wrap_non_dict_message(message)

        if self._messages_storage_manager.is_message_larger_than_1mb(message):
            message = self._messages_storage_manager.store_message(message, encode_result=False)
            self._logger.info(
                'Message received in rpc_request() was larger than 1MB so it was stored with '
                f'{type(self._messages_storage_manager).__name__}. The token needed to recover it is '
                f'{message["token"]}.'
            )

        message = json.dumps(message, default=str, separators=(',', ':'))
        rpc_response = await self._producer.rpc_request(topic, message, timeout)

        if rpc_response.get('is_stored') is True:
            rpc_response = self._messages_storage_manager.recover_message(rpc_response, encode_result=False)

        return rpc_response

    def __check_large_messages_decorator(self, func: Callable) -> Callable:
        async def inner_fn(message: NATSMessage):
            event = json.loads(message.data)
            if event.get("is_stored") is True:
                message.data = self._messages_storage_manager.recover_message(event, encode_result=True)
                self._logger.info(
                    f'Message received from topic {event} indicates that the actual message was larger than 1MB '
                    f'and was stored with {type(self._messages_storage_manager).__name__}. '
                    f'The original message (truncated) is "{json.dumps(event)[:200]}..."'
                )

            await func(message)

        return inner_fn

    def add_consumer(self, consumer: NATSClient, consumer_name: str):
        if self._consumers.get(consumer_name) is not None:
            self._logger.error(f'Consumer name {consumer_name} already registered. Skipping...')
            return

        consumer._cb_with_action = self.__check_large_messages_decorator(consumer._cb_with_action)
        self._consumers[consumer_name] = consumer

    def set_producer(self, producer: NATSClient):
        self._producer = producer

    async def connect(self):
        for consumer_name, consumer in self._consumers.items():
            await consumer.connect_to_nats()
        if self._producer is not None:
            await self._producer.connect_to_nats()

    async def subscribe_consumer(self, consumer_name: str, topic: str, action_wrapper: ActionWrapper, queue=""):
        await self._consumers.get(consumer_name).subscribe_action(topic, action_wrapper, queue)

    async def publish_message(self, topic, msg):
        if not isinstance(msg, dict):
            msg = self.__wrap_non_dict_message(msg)

        if self._messages_storage_manager.is_message_larger_than_1mb(msg):
            msg = self._messages_storage_manager.store_message(msg, encode_result=False)
            self._logger.info(
                'Message received in publish() was larger than 1MB so it was stored with '
                f'{type(self._messages_storage_manager).__name__}. The token needed to recover it is '
                f'{msg["token"]}.'
            )

        msg = json.dumps(msg, default=str, separators=(',', ':'))
        await self._producer.publish(topic, msg)

    async def close_connections(self):
        for consumer_name, consumer in self._consumers.items():
            await consumer.close_nats_connections()
        if self._producer is not None:
            await self._producer.close_nats_connections()
