from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN


class NatsStreamingClient:
    nc = None
    sc = None
    subs = list()

    async def connect_to_nats(self):
        # Use borrowed connection for NATS then mount NATS Streaming
        # client on top.
        self.nc = NATS()
        await self.nc.connect(servers=["nats://nats-streaming:4222"])
        # Start session with NATS Streaming cluster.
        self.sc = STAN()
        await self.sc.connect("automation-engine-nats", "client-123", nats=self.nc)

    async def publish_message(self, topic, message):
        await self.sc.publish(topic, message.encode())

    def _cb(self, msg):
        print("Received a message (seq={}): {}".format(msg.seq, msg.data))

    async def register_consumer(self, topic):
        sub = await self.sc.subscribe(topic, start_at='first', cb=self._cb)
        self.subs.append(sub)

    async def close_nats_connections(self):
        # Stop recieving messages
        for sub in self.subs:
            await sub.unsubscribe()
        # Close NATS Streaming session
        await self.sc.close()
        # We are using a NATS borrowed connection so we need to close manually.
        await self.nc.close()
