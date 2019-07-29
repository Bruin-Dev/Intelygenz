import json
from igz.packages.eventbus.eventbus import EventBus


class EventEdgesForAlert:

    def __init__(self, event_bus: EventBus, velocloud_repository, logger):
        self._event_bus = event_bus
        self._velocloud_repository = velocloud_repository
        self._logger = logger

    async def report_edge_event(self, msg):
        msg_dict = json.loads(msg)
        edgeids = msg_dict["edge"]
        start = msg_dict["start_date"]
        end = msg_dict["end_date"]
        limit = None
        if "limit" in msg_dict.keys():
            limit = msg_dict["limit"]

        self._logger.info(f'Sending events for edge with data {edgeids} for alerts')
        events_by_edge = self._velocloud_repository.get_all_edge_events(edgeids, start, end, limit)

        status = 200
        if events_by_edge is None:
            status = 204
        if isinstance(events_by_edge, Exception):
            status = 500

        edge_event_response = {"request_id": msg_dict['request_id'], "events": events_by_edge, "status": status}
        await self._event_bus.publish_message(msg_dict['response_topic'], json.dumps(edge_event_response, default=str))
        self._logger.info("Edge events sent")
