from asyncio import sleep as aiosleep
from asgiref.sync import async_to_sync
from config import config
from igz.packages.nats.clients import NatsStreamingClient
from prometheus_client import start_http_server, Summary
import random
import time


MESSAGES_PROCESSED = Summary('nats_processed_messages', 'Messages processed from NATS')

@MESSAGES_PROCESSED.time()
def print_callback(msg):
    print(msg)


@async_to_sync
async def run():
    nats_s_client = NatsStreamingClient(config)
    await nats_s_client.connect_to_nats()
    await nats_s_client.publish("basemicroservice", "Some message")
    await nats_s_client.publish("basemicroservice", "Some message2")
    await nats_s_client.publish("basemicroservice", "Some message3")
    await nats_s_client.subscribe(topic="basemicroservice", callback=print_callback)
    print("Waiting 5 seconds to consume messages...")
    await aiosleep(5)
    await nats_s_client.close_nats_connections()


REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

@REQUEST_TIME.time()
def process_request(t):
    """A dummy function that takes some time."""
    time.sleep(t)


if __name__ == '__main__':
    print("Base microservic starting...")
    run()

    # Start up the server to expose the metrics.
    start_http_server(9100)
    # Generate some requests.
    print('starting metrics loop')
    while True:
        process_request(random.random())
