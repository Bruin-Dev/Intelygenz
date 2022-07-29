import json
import logging
import sys
from typing import Callable

from igz.packages.eventbus.action import ActionWrapper
from igz.packages.nats.clients import NATSClient
from nats.aio.client import Msg as NATSMessage


class EventBus:
    _consumers = None
    _producer = None
    _logger = None

    def __init__(self, messages_storage_manager, logger=None):
        self._consumers = dict()
        self._messages_storage_manager = messages_storage_manager
        if logger is None:
            logger = logging.getLogger("event-bus")
            logger.setLevel(logging.DEBUG)
            log_handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter("%(asctime)s: %(module)s: %(levelname)s: %(message)s")
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
                "Message received in rpc_request() was larger than 1MB so it was stored with "
                f"{type(self._messages_storage_manager).__name__}. The token needed to recover it is "
                f'{message["token"]}.'
            )

        message = json.dumps(message, default=str, separators=(",", ":"))

        self._logger.info(f"Requesting a response from subject {topic}...")
        rpc_response = await self._producer.rpc_request(topic, message, timeout)
        self._logger.info(f"Response received from a replier subscribed to subject {topic}")

        if rpc_response.get("is_stored") is True:
            self._logger.info(
                f"Message received from topic {topic} indicates that the actual message was larger than 1MB "
                f"and was stored with {type(self._messages_storage_manager).__name__}."
            )
            rpc_response = self._messages_storage_manager.recover_message(rpc_response, encode_result=False)

        return rpc_response

    def __check_large_messages_decorator(self, func: Callable) -> Callable:
        async def inner_fn(message: NATSMessage):
            event = json.loads(message.data)
            if event.get("is_stored") is True:
                message.data = self._messages_storage_manager.recover_message(event, encode_result=True)
                self._logger.info(
                    f"Message received from topic {event} indicates that the actual message was larger than 1MB "
                    f"and was stored with {type(self._messages_storage_manager).__name__}."
                )

            await func(message)

        return inner_fn

    def add_consumer(self, consumer: NATSClient, consumer_name: str):
        self._logger.info(f"Adding consumer {consumer_name} to the event bus...")
        if self._consumers.get(consumer_name) is not None:
            self._logger.error(f"Consumer name {consumer_name} already registered. Skipping...")
            return

        consumer._cb_with_action = self.__check_large_messages_decorator(consumer._cb_with_action)
        self._consumers[consumer_name] = consumer
        self._logger.info(f"Consumer {consumer_name} added to the event bus")

    def set_producer(self, producer: NATSClient):
        self._producer = producer

    async def connect(self):
        self._logger.info(f"Establishing connection to NATS for all consumers...")
        for consumer_name, consumer in self._consumers.items():
            await consumer.connect_to_nats()
        self._logger.info(f"Connection to NATS established successfully for all consumers")

        if self._producer is not None:
            self._logger.info(f"Establishing connection to NATS for producer...")
            await self._producer.connect_to_nats()
            self._logger.info(f"Connection to NATS established successfully for producer")

    async def subscribe_consumer(self, consumer_name: str, topic: str, action_wrapper: ActionWrapper, queue=""):
        self._logger.info(
            f"Subscribing consumer {consumer_name} from the event bus to subject {topic} and adding it under NATS "
            f"queue {queue}..."
        )
        await self._consumers.get(consumer_name).subscribe_action(topic, action_wrapper, queue)
        self._logger.info(f"Consumer {consumer_name} from the event bus subscribed successfully")

    async def publish_message(self, topic, msg):
        self._logger.info(f"Publishing message to subject {topic}...")

        if not isinstance(msg, dict):
            msg = self.__wrap_non_dict_message(msg)

        if self._messages_storage_manager.is_message_larger_than_1mb(msg):
            msg = self._messages_storage_manager.store_message(msg, encode_result=False)
            self._logger.info(
                "Message received in publish() was larger than 1MB so it was stored with "
                f"{type(self._messages_storage_manager).__name__}. The token needed to recover it is "
                f'{msg["token"]}.'
            )

        msg = json.dumps(msg, default=str, separators=(",", ":"))
        await self._producer.publish(topic, msg)

        self._logger.info(f"Message published to subject {topic} successfully")

    async def close_connections(self):
        self._logger.info("Closing connection for all consumers in the event bus...")
        for consumer_name, consumer in self._consumers.items():
            await consumer.close_nats_connections()
        self._logger.info("Connections closed for all consumers in the event bus")

        if self._producer is not None:
            self._logger.info("Closing connection for producer in the event bus...")
            await self._producer.close_nats_connections()
            self._logger.info("Closed connection for producer in the event bus")
