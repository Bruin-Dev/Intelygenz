from asgiref.sync import async_to_sync
from config import config
from igz.packages.nats.clients import NatsStreamingClient
import velocloud
import os
import asyncio

publisher = NatsStreamingClient(config, "velocloud-drone-publisher")
velocloud.configuration.verify_ssl = False
client = velocloud.ApiClient(host=os.environ["VELOCLOUD_HOST"])
client.authenticate(os.environ["VELOCLOUD_USER"], os.environ["VELOCLOUD_PASS"], operator=True)
api = velocloud.AllApi(client)


def process_edge(edgeids):
    try:
        res = api.edgeGetEdge(body=edgeids)
    except velocloud.rest.ApiException as e:
        print(e)
    return res


def report_edge_status(msg):
    import json
    edgeids = json.loads(msg.decode("utf-8").replace("\\", ' ').replace("'", '"'))
    print(f'Processing edge with data {msg}')
    edge_status = process_edge(edgeids)
    print(f'Got edge status from Velocloud: {edge_status}')

    if edge_status._edgeState is 'CONNECTED':
        print('Edge seems OK, sending it to topic edge.status.ok')
        topic = "edge.status.ok"
    else:
        print('Edge seems KO, failure! Sending it to topic edge.status.ko')
        topic = "edge.status.ko"
    loop = asyncio.new_event_loop()
    loop.run_until_complete(publisher.publish(topic, repr(edge_status)))
    loop.close()


async def connect_to_event_bus(subscriber):
    await publisher.connect_to_nats()
    await subscriber.connect_to_nats()
    await subscriber.subscribe(topic="edge.status.task", callback=report_edge_status, durable_name="velocloud_drones",
                               queue='velocloud_drones')


@async_to_sync
async def run():
    subscriber = NatsStreamingClient(config, "velocloud-drone-subscriber")
    await connect_to_event_bus(subscriber)


if __name__ == '__main__':
    print("Velocloud drone starting...")
    run()
    loop = asyncio.new_event_loop()
    loop.run_forever()
