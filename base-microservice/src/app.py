from asyncio import sleep as aiosleep
from asgiref.sync import async_to_sync
from config import config
from igz.packages.nats.clients import NatsStreamingClient


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


if __name__ == '__main__':
    print("Base microservic starting...")
    # velocloud_hello_world()
    run()
