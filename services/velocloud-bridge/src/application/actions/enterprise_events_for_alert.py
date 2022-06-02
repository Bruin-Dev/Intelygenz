import json

from igz.packages.eventbus.eventbus import EventBus


class EventEnterpriseForAlert:
    def __init__(self, event_bus: EventBus, velocloud_repository, logger):
        self._event_bus = event_bus
        self._velocloud_repository = velocloud_repository
        self._logger = logger

    async def report_enterprise_event(self, msg: dict):
        enterprise_event_response = {"request_id": msg["request_id"], "body": None, "status": None}
        if msg.get("body") is None:
            enterprise_event_response["status"] = 400
            enterprise_event_response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg["response_topic"], enterprise_event_response)
            return
        if all(key in msg["body"].keys() for key in ("enterprise_id", "host", "start_date", "end_date")):
            enterprise_id = msg["body"]["enterprise_id"]
            host = msg["body"]["host"]
            start = msg["body"]["start_date"]
            end = msg["body"]["end_date"]
            limit = None
            filter = None

            if "filter" in msg["body"].keys():
                filter = msg["body"]["filter"]

            if "limit" in msg["body"].keys():
                limit = msg["body"]["limit"]

            self._logger.info(f"Sending events for enterprise with data {enterprise_id} for alerts")
            events_by_enterprise = await self._velocloud_repository.get_all_enterprise_events(
                enterprise_id, host, start, end, limit, filter
            )
            enterprise_event_response["body"] = events_by_enterprise["body"]
            enterprise_event_response["status"] = events_by_enterprise["status"]

            self._logger.info(
                f"Enterprise events for alerts published in event bus for request {json.dumps(msg)}. "
                f"Message published was {enterprise_event_response}"
            )
        else:
            enterprise_event_response["status"] = 400
            enterprise_event_response["body"] = (
                'Must include "enterprise_id", "host", "start_date", "end_date" ' "in request"
            )
        await self._event_bus.publish_message(msg["response_topic"], enterprise_event_response)
