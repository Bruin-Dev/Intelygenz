from asyncio import sleep as aiosleep
from asgiref.sync import async_to_sync
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN


class NATSConnector:
    nc = None
    sc = None

    async def connect_to_nats(self):
        # Use borrowed connection for NATS then mount NATS Streaming
        # client on top.
        self.nc = NATS()
        await self.nc.connect(servers=["nats://nats-streaming:4222"])

        # Start session with NATS Streaming cluster.
        self.sc
        self.sc = STAN()
        await self.sc.connect("automation-engine-nats", "client-123", nats=self.nc)

    async def publish_message(self,topic, message):
        await self.sc.publish(topic, message)

    async def _cb(self, msg):
        print("Received a message (seq={}): {}".format(msg.seq, msg.data))

    async def register_consumer(self, topic):
        global sub
        sub = await self.sc.subscribe(topic, start_at='first', cb=self._cb)

    async def close_nats_connections(self):
        # Stop recieving messages
        await sub.unsubscribe()
        # Close NATS Streaming session
        await self.sc.close()

        # We are using a NATS borrowed connection so we need to close manually.
        await self.nc.close()


@async_to_sync
async def run():
    nats_connector = NATSConnector()
    await nats_connector.connect_to_nats()
    await nats_connector.publish_message("Some-topic", b'Some message')
    await nats_connector.publish_message("Some-topic", b'Some message2')
    await nats_connector.publish_message("Some-topic", b'Some message3')
    await nats_connector.register_consumer("Some-topic")
    print("Waiting 5 seconds to consume messages...")
    await aiosleep(5)
    await nats_connector.close_nats_connections()


if __name__ == '__main__':
    print("Bruin bridge starting...")
    run()
