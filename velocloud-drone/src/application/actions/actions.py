from igz.packages.eventbus.eventbus import EventBus
from igz.packages.Logger.logger_client import LoggerClient
import velocloud
import json


class Actions:
    event_bus = None
    velocloud_repository = None

    def __init__(self, event_bus: EventBus, velocloud_repository):
        self.event_bus = event_bus
        self.velocloud_repository = velocloud_repository

    def _process_edge(self, edgeids):
        edge_status = None
        try:
            edge_status = self.velocloud_repository.get_edge_information(edgeids['host'],
                                                                         edgeids['enterpriseId'],
                                                                         edgeids['id'])
        except velocloud.rest.ApiException as e:
            print(e)
        return edge_status

    async def report_edge_status(self, msg):
        edgeids = json.loads(msg.decode("utf-8").replace("\\", ' ').replace("'", '"'))
        print(f'Processing edge with data {msg}')
        edge_status = self._process_edge(edgeids)
        print(f'Got edge status from Velocloud: {edge_status}')

        if edge_status._edgeState == 'CONNECTED':
            print('Edge seems OK, sending it to topic edge.status.ok')
            topic = "edge.status.ok"
        else:
            print('Edge seems KO, failure! Sending it to topic edge.status.ko')
            topic = "edge.status.ko"
        await self.event_bus.publish_message(topic, repr(edge_status))
