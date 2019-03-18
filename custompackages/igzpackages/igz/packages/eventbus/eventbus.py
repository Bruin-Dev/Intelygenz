from igz.packages.nats.clients import NatsStreamingClient
from igz.packages.eventbus.action import ActionWrapper
import logging
import sys


class EventBus:
    _consumers = None
    _producer = None
    _logger = None

    def __init__(self, logger=None):
        self._consumers = dict()
        if logger is None:
            logging.basicConfig(level=logging.DEBUG, format='%(asctime)s: %(module)s: %(levelname)s: %(message)s',
                                handlers=[logging.StreamHandler(sys.stdout)])
            logger = logging.getLogger('event-bus')
        self._logger = logger

    def add_consumer(self, consumer: NatsStreamingClient, consumer_name: str):
        if self._consumers.get(consumer_name) is not None:
            self._logger.error(f'Consumer name {consumer_name} already registered. Skipping...')
            return
        self._consumers[consumer_name] = consumer

    def set_producer(self, producer: NatsStreamingClient):
        self._producer = producer

    async def connect(self):
        for consumer_name, consumer in self._consumers.items():
            await consumer.connect_to_nats()
        if self._producer is not None:
            await self._producer.connect_to_nats()

    async def subscribe_consumer(self, consumer_name: str, topic: str, action_wrapper: ActionWrapper, start_at='first',
                                 time=None, sequence=None, queue=None, durable_name=None):
        await self._consumers.get(consumer_name).subscribe_action(topic, action_wrapper, start_at, time, sequence,
                                                                  queue,
                                                                  durable_name)

    async def publish_message(self, topic, msg):
        await self._producer.publish(topic, msg)

    async def close_connections(self):
        for consumer_name, consumer in self._consumers.items():
            await consumer.close_nats_connections()
        if self._producer is not None:
            await self._producer.close_nats_connections()
