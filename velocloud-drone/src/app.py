from asgiref.sync import async_to_sync
from config import config
from igz.packages.nats.clients import NatsStreamingClient
from igz.packages.eventbus.eventbus import EventBus
from igz.packages.eventbus.action import ActionWrapper
import velocloud
import os
import asyncio


class Actions:
    event_bus = None
    velocloud_client = None

    def __init__(self, event_bus: EventBus, velocloud_client):
        self.event_bus = event_bus
        self.velocloud_client = velocloud_client

    def _process_edge(self, edgeids):
        try:
            res = self.velocloud_client.edgeGetEdge(body=edgeids)
        except velocloud.rest.ApiException as e:
            print(e)
        return res

    async def report_edge_status(self, msg):
        import json
        edgeids = json.loads(msg.decode("utf-8").replace("\\", ' ').replace("'", '"'))
        print(f'Processing edge with data {msg}')
        edge_status = self._process_edge(edgeids)
        print(f'Got edge status from Velocloud: {edge_status}')

        if edge_status._edgeState is 'CONNECTED':
            print('Edge seems OK, sending it to topic edge.status.ok')
            topic = "edge.status.ok"
        else:
            print('Edge seems KO, failure! Sending it to topic edge.status.ko')
            topic = "edge.status.ko"
        await self.event_bus.publish_message(topic, repr(edge_status))


class Container:
    velocloud_client = None
    publisher = None
    subscriber = None
    event_bus = None
    report_edge_action = None

    def setup(self):
        velocloud.configuration.verify_ssl = False
        client = velocloud.ApiClient(host=os.environ["VELOCLOUD_HOST"])
        client.authenticate(os.environ["VELOCLOUD_USER"], os.environ["VELOCLOUD_PASS"], operator=True)
        self.velocloud_client = velocloud.AllApi(client)

        self.publisher = NatsStreamingClient(config, "velocloud-drone-publisher")
        self.subscriber = NatsStreamingClient(config, "velocloud-drone-subscriber")

        self.event_bus = EventBus()
        self.event_bus.add_consumer(self.subscriber, consumer_name="tasks")
        self.event_bus.set_producer(self.publisher)

        self.report_edge_action = ActionWrapper(Actions(self.event_bus, self.velocloud_client), "report_edge_status",
                                                is_async=True)

    async def start(self):
        await self.event_bus.connect()
        await self.event_bus.subscribe_consumer(consumer_name="tasks", topic="edge.status.task",
                                                action_wrapper=self.report_edge_action, durable_name="velocloud_drones",
                                                queue="velocloud_drones")

    async def run(self):
        self.setup()
        await self.start()


if __name__ == '__main__':
    print("Velocloud drone starting...")
    loop = asyncio.get_event_loop()
    container = Container()
    loop.run_until_complete(container.run())
    loop.run_forever()
