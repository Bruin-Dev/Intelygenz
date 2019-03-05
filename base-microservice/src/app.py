from asgiref.sync import async_to_sync
from config import config
from igz.packages.nats.clients import NatsStreamingClient
from prometheus_client import start_http_server, Summary
import time
import asyncio

MESSAGES_PROCESSED = Summary('nats_processed_messages', 'Messages processed from NATS')
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')


@MESSAGES_PROCESSED.time()
def durable_print_callback(msg):
    print('Im one of the members of the durable group!')


@REQUEST_TIME.time()
def first_print_callback(msg):
    print('Im not a member of the durable group. I start_at=first')
    print(msg)


class Container:
    client1 = None
    client2 = None
    client3 = None
    client4 = None

    @async_to_sync
    async def run(self):
        self.setup()
        await self.start()

    def setup(self):
        self.client1 = NatsStreamingClient(config, "base-microservice-client")
        self.client2 = NatsStreamingClient(config, "base-microservice-client2")
        self.client3 = NatsStreamingClient(config, "base-microservice-client3")
        self.client4 = NatsStreamingClient(config, "base-microservice-client4")

    async def start(self):
        # Start up the server to expose the metrics.
        start_http_server(9100)
        # Generate some requests.
        print('starting metrics loop')

        await self.client1.connect_to_nats()
        await self.client2.connect_to_nats()
        await self.client3.connect_to_nats()
        await self.client4.connect_to_nats()

        await self.client1.publish("topic1", "Message 1")
        await self.client1.publish("topic1", "Message 2")
        await self.client1.publish("topic1", "Message 3")

        await self.client4.subscribe(topic="topic1", callback=first_print_callback,
                                     start_at='first')
        await self.client2.subscribe(topic="topic1", callback=durable_print_callback, durable_name="name",
                                     queue="queue",
                                     start_at='first')
        await self.client3.subscribe(topic="topic1", callback=durable_print_callback, durable_name="name",
                                     queue="queue",
                                     start_at='first')


REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')


@REQUEST_TIME.time()
def process_request(t):
    """A dummy function that takes some time."""
    time.sleep(t)


if __name__ == '__main__':
    print("Base microservic starting...")
    container = Container()
    container.run()
    loop = asyncio.new_event_loop()
    loop.run_forever()
