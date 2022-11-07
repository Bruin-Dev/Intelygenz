import json
import logging

from dateutil.parser import parse
from nats.aio.msg import Msg
from pytz import utc

from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class GetCustomers:
    def __init__(self, config, storage_repository):
        self._config = config
        self._storage_repository = storage_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        logger.info(f"Getting customers...")
        response = {"body": None, "status": None}

        if "body" not in payload.keys():
            logger.error(f"Cannot get customer cache using {json.dumps(payload)}. JSON malformed")
            response["status"] = 400
            response["body"] = 'You must specify {.."body":{...}} in the request'
            await msg.respond(to_json_bytes(response))
            return

        body = payload["body"]

        last_contact_filter = body["last_contact_filter"] if "last_contact_filter" in body else None
        cache = self._storage_repository.get_hawkeye_cache()
        if len(cache) == 0:
            logger.warning(f"Cache is still being built")
            response["body"] = f"Cache is still being built"
            response["status"] = 202
            await msg.respond(to_json_bytes(response))
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
            logger.warning(f"No devices were found for the specified filters: {body}")
            response["body"] = f"No devices were found for the specified filters: {body}"
            response["status"] = 404
            await msg.respond(to_json_bytes(response))
            return
        else:
            logger.info(f"{len(filter_cache)} devices were found for the specified filters: {body}")
            response["body"] = filter_cache
            response["status"] = 200

        await msg.respond(to_json_bytes(response))
        logger.info(f"Get customer response published in event bus")
