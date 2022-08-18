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
            response["body"] = "You must specify " '{.."body":{"filter":[...]}} in the request'
            await self._event_bus.publish_message(response_topic, response)
            return
        body = msg["body"]
        if "filter" not in body.keys():
            self._logger.error(f'Cannot get customer cache info using {json.dumps(body)}. Need "filter"')
            response["status"] = 400
            response["body"] = 'You must specify "filter" in the body'
            await self._event_bus.publish_message(response_topic, response)
            return

        filters = body["filter"]
        last_contact_filter = body["last_contact_filter"] if "last_contact_filter" in body else None
        caches = self._storage_repository.get_host_cache(filters=filters)
        if len(caches) == 0:
            response["body"] = f'Cache is still being built for host(s): {", ".join(body["filter"].keys())}'
            response["status"] = 202
            await self._event_bus.publish_message(msg["response_topic"], response)
            return
        filter_cache = (
            [
                edge
                for edge in caches
                if parse(last_contact_filter).astimezone(utc) < parse(edge["last_contact"]).astimezone(utc)
            ]
            if last_contact_filter is not None
            else caches
        )

        if len(filter_cache) == 0:
            response["body"] = "No edges were found for the specified filters"
            response["status"] = 404
            await self._event_bus.publish_message(msg["response_topic"], response)
            return
        else:
            response["body"] = filter_cache
            response["status"] = 200
        await self._event_bus.publish_message(msg["response_topic"], response)
        self._logger.info(f"Get customer response published in event bus")
