from asyncio import sleep as aiosleep
from asgiref.sync import async_to_sync
from config import config
from igz.packages.nats.clients import NatsStreamingClient


def report_edge_status(msg):
    print(f'Processing edge with data {msg}')


async def subscribe_to_nats(natsclient):
    await natsclient.connect_to_nats()
    await natsclient.subscribe(topic="edge.status.request", callback=report_edge_status)


@async_to_sync
async def run():
    nats_s_client = NatsStreamingClient(config)
    await subscribe_to_nats(nats_s_client)

    print("Waiting 10 seconds to consume all messages...")
    await aiosleep(10)
    await nats_s_client.close_nats_connections()


if __name__ == '__main__':
    print("Velocloud drone starting...")
    run()
