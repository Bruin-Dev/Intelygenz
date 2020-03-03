from igz.packages.eventbus.eventbus import EventBus
import json


class EventEdgesForAlert:

    def __init__(self, event_bus: EventBus, velocloud_repository, logger):
        self._event_bus = event_bus
        self._velocloud_repository = velocloud_repository
        self._logger = logger

    async def report_edge_event(self, msg: dict):
        edge_event_response = {"request_id": msg['request_id'], "body": None,
                               "status": None}
        if msg.get("body") is None:
            edge_event_response["status"] = 400
            edge_event_response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg['response_topic'], edge_event_response)
            return
        if all(key in msg['body'].keys() for key in ("edge", "start_date", "end_date")):
            edgeids = msg["body"]["edge"]
            start = msg["body"]["start_date"]
            end = msg["body"]["end_date"]
            limit = None
            filter = None

            if "filter" in msg["body"].keys():
                filter = msg["body"]["filter"]

            if "limit" in msg["body"].keys():
                limit = msg["body"]["limit"]

            self._logger.info(f'Sending events for edge with data {edgeids} for alerts')
            events_by_edge = self._velocloud_repository.get_all_edge_events(edgeids, start, end, limit, filter)
            edge_event_response["body"] = events_by_edge["body"]
            edge_event_response["status"] = events_by_edge["status"]

            self._logger.info(
                f'Edge events for alerts published in event bus for request {json.dumps(msg)}. '
                f"Message published was {edge_event_response}"
            )
        else:
            edge_event_response["status"] = 400
            edge_event_response["body"] = 'Must include "edge", "start_date", "end_date" in request'
        await self._event_bus.publish_message(msg['response_topic'], edge_event_response)
