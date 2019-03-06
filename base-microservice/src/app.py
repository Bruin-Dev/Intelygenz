from asgiref.sync import async_to_sync
from config import config
from igz.packages.nats.clients import NatsStreamingClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.action import ActionWrapper
from prometheus_client import start_http_server, Summary
import time
import asyncio

MESSAGES_PROCESSED = Summary('nats_processed_messages', 'Messages processed from NATS')
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')


class DurableAction:
    def durable_print_callback(self, msg):
        print('DURABLE GROUP')
        print(msg)


@MESSAGES_PROCESSED.time()
def durable_print_callback(msg):
    print('Im one of the members of the durable group!')


class FromFirstAction:
    def first_print_callback(self, msg):
        print('SUBSCRIBER FROM FIRST')
        print(msg)


@REQUEST_TIME.time()
def first_print_callback(msg):
    print('Im not a member of the durable group. I start_at=first')
    print(msg)


class Container:
    client1 = None
    client2 = None
    client3 = None
    client4 = None
    event_bus = None
    durable_action = None
    from_first_action = None

    @async_to_sync
    async def run(self):
        self.setup()
        await self.start()

    def setup(self):
        self.client1 = NatsStreamingClient(config, "base-microservice-client")
        self.client2 = NatsStreamingClient(config, "base-microservice-client2")
        self.client3 = NatsStreamingClient(config, "base-microservice-client3")
        self.client4 = NatsStreamingClient(config, "base-microservice-client4")

        base_durable_action = DurableAction()
        base_from_first_action = FromFirstAction()

        self.durable_action = ActionWrapper(base_durable_action, "durable_print_callback")
        self.from_first_action = ActionWrapper(base_from_first_action, "first_print_callback")

        self.event_bus = EventBus()

        self.event_bus.set_producer(self.client1)

        self.event_bus.add_consumer(consumer=self.client2, consumer_name="consumer2")
        self.event_bus.add_consumer(consumer=self.client3, consumer_name="consumer3")
        self.event_bus.add_consumer(consumer=self.client4, consumer_name="consumer4")

    async def start(self):
        await self.event_bus.connect()

        # Start up the server to expose the metrics.
        start_http_server(9100)
        # Generate some requests.
        print('starting metrics loop')

        await self.event_bus.publish_message("topic1", "Message 1")
        await self.event_bus.publish_message("topic1", "Message 2")
        await self.event_bus.publish_message("topic1", "Message 3")

        await self.event_bus.subscribe_consumer(consumer_name="consumer4", topic="topic1",
                                                action_wrapper=self.from_first_action,
                                                start_at='first')

        await self.event_bus.subscribe_consumer(consumer_name="consumer3", topic="topic1",
                                                action_wrapper=self.durable_action,
                                                durable_name="name",
                                                queue="queue",
                                                start_at='first')

        await self.event_bus.subscribe_consumer(consumer_name="consumer2", topic="topic1",
                                                action_wrapper=self.durable_action,
                                                durable_name="name",
                                                queue="queue",
                                                start_at='first')


if __name__ == '__main__':
    print("Base microservic starting...")
    container = Container()
    container.run()
    loop = asyncio.new_event_loop()
    loop.run_forever()
