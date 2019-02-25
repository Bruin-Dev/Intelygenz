from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN


class NatsStreamingClient:
    nc = None
    sc = None
    subs = list()
    config = None

    def __init__(self, config):
        self.config = config

    async def connect_to_nats(self):
        # Use borrowed connection for NATS then mount NATS Streaming
        # client on top.
        self.nc = NATS()
        await self.nc.connect(servers=self.config.NATS_CONFIG["servers"])
        # Start session with NATS Streaming cluster.
        self.sc = STAN()
        await self.sc.connect(self.config.NATS_CONFIG["cluster_name"], self.config.NATS_CONFIG["client_ID"], nats=self.nc)

    async def publish_message(self, topic, message):
        await self.sc.publish(topic, message.encode())

    def _cb(self, msg):
        print(f'Received a message (seq={msg.seq}): {msg.data.decode()}')

    async def register_consumer(self):
        sub = await self.sc.subscribe(self.config.NATS_CONFIG["consumer"]["topic"],
                                      start_at=self.config.NATS_CONFIG["consumer"]["start_at"], cb=self._cb)
        self.subs.append(sub)

    async def close_nats_connections(self):
        # Stop recieving messages
        for sub in self.subs:
            await sub.unsubscribe()
        # Close NATS Streaming session
        await self.sc.close()
        # We are using a NATS borrowed connection so we need to close manually.
        await self.nc.close()
