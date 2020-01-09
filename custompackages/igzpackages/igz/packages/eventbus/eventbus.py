from igz.packages.nats.clients import NATSClient
from igz.packages.eventbus.action import ActionWrapper
import logging
import sys
import json


class EventBus:
    _consumers = None
    _producer = None
    _logger = None

    def __init__(self, logger=None):
        self._consumers = dict()
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

        message = json.dumps(message, default=str, separators=(',', ':'))
        return await self._producer.rpc_request(topic, message, timeout)

    def add_consumer(self, consumer: NATSClient, consumer_name: str):
        if self._consumers.get(consumer_name) is not None:
            self._logger.error(f'Consumer name {consumer_name} already registered. Skipping...')
            return
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

        msg = json.dumps(msg, default=str, separators=(',', ':'))
        await self._producer.publish(topic, msg)

    async def close_connections(self):
        for consumer_name, consumer in self._consumers.items():
            await consumer.close_nats_connections()
        if self._producer is not None:
            await self._producer.close_nats_connections()
