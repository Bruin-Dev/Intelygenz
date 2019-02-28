from asyncio import sleep as aiosleep
from asgiref.sync import async_to_sync
from config import config
from igz.packages.nats.clients import NatsStreamingClient


def print_callback(msg):
    print('Detected faulty edge. Taking notification actions...')
    print(msg)


@async_to_sync
async def run():
    nats_s_client = NatsStreamingClient(config, "velocloud-notificator-subscriber")
    await nats_s_client.connect_to_nats()
    await nats_s_client.subscribe(topic="edge.status.ko", callback=print_callback)
    delay = 10
    print(f'Waiting {delay} seconds to consume messages...')
    await aiosleep(delay)
    await nats_s_client.close_nats_connections()


if __name__ == '__main__':
    print("Velocloud notificator starting...")
    run()
