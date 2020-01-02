from igz.packages.eventbus.eventbus import EventBus


class EventEdgesForAlert:

    def __init__(self, event_bus: EventBus, velocloud_repository, logger):
        self._event_bus = event_bus
        self._velocloud_repository = velocloud_repository
        self._logger = logger

    async def report_edge_event(self, msg: dict):
        edgeids = msg["edge"]
        start = msg["start_date"]
        end = msg["end_date"]
        limit = None
        filter = None

        if "filter" in msg.keys():
            filter = msg["filter"]

        if "limit" in msg.keys():
            limit = msg["limit"]

        self._logger.info(f'Sending events for edge with data {edgeids} for alerts')
        events_by_edge = self._velocloud_repository.get_all_edge_events(edgeids, start, end, limit, filter)

        status = 200
        if events_by_edge is None:
            status = 204
        if isinstance(events_by_edge, Exception):
            status = 500

        edge_event_response = {"request_id": msg['request_id'], "events": events_by_edge, "status": status}
        await self._event_bus.publish_message(msg['response_topic'], edge_event_response)
        self._logger.info("Edge events sent")
