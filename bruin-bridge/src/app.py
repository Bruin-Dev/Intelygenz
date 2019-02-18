from application.clients.nats_streaming_client import NatsStreamingClient
from asyncio import sleep as aiosleep
from asgiref.sync import async_to_sync


@async_to_sync
async def run():
    nats_s_client = NatsStreamingClient()
    await nats_s_client.connect_to_nats()
    await nats_s_client.publish_message("Some-topic", b'Some message')
    await nats_s_client.publish_message("Some-topic", b'Some message2')
    await nats_s_client.publish_message("Some-topic", b'Some message3')
    await nats_s_client.register_consumer("Some-topic")
    print("Waiting 5 seconds to consume messages...")
    await aiosleep(5)
    await nats_s_client.close_nats_connections()


if __name__ == '__main__':
    print("Bruin bridge starting...")
    run()
