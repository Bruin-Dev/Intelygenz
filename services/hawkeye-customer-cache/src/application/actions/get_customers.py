import json

from dateutil.parser import parse
from pytz import utc


class GetCustomers:
    def __init__(self, config, logger, storage_repository, event_bus):
        self._config = config
        self._logger = logger
        self._storage_repository = storage_repository
        self._event_bus = event_bus

    async def get_customers(self, msg: dict):
        self._logger.info(f"Getting customers...")
        request_id = msg["request_id"]
        response_topic = msg["response_topic"]
        response = {"request_id": request_id, "body": None, "status": None}

        if "body" not in msg.keys():
            self._logger.error(f"Cannot get customer cache using {json.dumps(msg)}. JSON malformed")
            response["status"] = 400
            response["body"] = 'You must specify {.."body":{...}} in the request'
            await self._event_bus.publish_message(response_topic, response)
            return
        body = msg["body"]

        last_contact_filter = body["last_contact_filter"] if "last_contact_filter" in body else None
        cache = self._storage_repository.get_hawkeye_cache()
        if len(cache) == 0:
            response["body"] = f"Cache is still being built"
            response["status"] = 202
            await self._event_bus.publish_message(msg["response_topic"], response)
            return
        filter_cache = (
            [
                device
                for device in cache
                if parse(last_contact_filter).astimezone(utc) < parse(device["last_contact"]).astimezone(utc)
            ]
            if last_contact_filter is not None
            else cache
        )

        if len(filter_cache) == 0:
            response["body"] = "No devices were found for the specified filters"
            response["status"] = 404
            await self._event_bus.publish_message(msg["response_topic"], response)
            return
        else:
            response["body"] = filter_cache
            response["status"] = 200
        await self._event_bus.publish_message(msg["response_topic"], response)
        self._logger.info(f"Get customer response published in event bus")
