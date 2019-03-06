from igz.packages.nats.clients import NatsStreamingClient
from igz.packages.eventbus.action import ActionWrapper


class EventBus:
    _consumers = None
    _producer = None

    def __init__(self):
        self._consumers = dict()

    def add_consumer(self, consumer: NatsStreamingClient, consumer_name: str):
        if self._consumers.get(consumer_name) is not None:
            print(f'Consumer name {consumer_name} already registered. Skipping...')
            return
        self._consumers[consumer_name] = consumer

    def set_producer(self, producer: NatsStreamingClient):
        self._producer = producer

    async def connect(self):
        for consumer_name, consumer in self._consumers.items():
            await consumer.connect_to_nats()
        await self._producer.connect_to_nats()

    async def subscribe_consumer(self, consumer_name: str, topic: str, action_wrapper: ActionWrapper, start_at='first',
                                 time=None, sequence=None, queue=None, durable_name=None):
        await self._consumers.get(consumer_name).subscribe_action(topic, action_wrapper, start_at, time, sequence,
                                                                  queue,
                                                                  durable_name)
        pass

    async def publish_message(self, topic, msg):
        await self._producer.publish(topic, msg)

    async def close_connections(self):
        for consumer_name, consumer in self._consumers.items():
            await consumer.close_nats_connections()
        await self._producer.close_nats_connections()
