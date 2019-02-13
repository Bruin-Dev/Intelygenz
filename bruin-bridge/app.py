from asyncio import sleep as aiosleep
from asgiref.sync import async_to_sync
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN


async def connect_to_nats():
    # Use borrowed connection for NATS then mount NATS Streaming
    # client on top.
    global nc
    nc = NATS()
    await nc.connect(servers=["nats://nats-streaming:4222"])

    # Start session with NATS Streaming cluster.
    global sc
    sc = STAN()
    await sc.connect("automation-engine-nats", "client-123", nats=nc)


async def publish_message(topic, message):
    await sc.publish(topic, message)


async def cb(msg):
    print("Received a message (seq={}): {}".format(msg.seq, msg.data))


async def register_consumer(topic):
    global sub
    sub = await sc.subscribe(topic, start_at='first', cb=cb)


async def close_nats_connections():
    # Stop recieving messages
    await sub.unsubscribe()
    # Close NATS Streaming session
    await sc.close()

    # We are using a NATS borrowed connection so we need to close manually.
    await nc.close()


@async_to_sync
async def run():
    await connect_to_nats()
    await publish_message("Some-topic", b'Some message')
    await publish_message("Some-topic", b'Some message2')
    await publish_message("Some-topic", b'Some message3')
    await register_consumer("Some-topic")
    print("Waiting 5 seconds to consume messages...")
    await aiosleep(5)
    await close_nats_connections()


if __name__ == '__main__':
    print("Bruin bridge starting...")
    run()
