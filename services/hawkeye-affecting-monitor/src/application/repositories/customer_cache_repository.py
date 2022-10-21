import json
import logging
from datetime import datetime, timedelta

from shortuuid import uuid

from application import nats_error_response
from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class CustomerCacheRepository:
    def __init__(self, nats_client, config, notifications_repository):
        self._nats_client = nats_client
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_cache(self, *, last_contact_filter: str = None):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {},
        }

        if last_contact_filter:
            request["body"]["last_contact_filter"] = last_contact_filter

        try:
            logger.info(f"Getting customer cache for Hawkeye...")
            response = await self._nats_client.request("hawkeye.customer.cache.get", to_json_bytes(request), timeout=60)
            response = json.loads(response.data)
        except Exception as e:
            err_msg = f"An error occurred when requesting customer cache -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status not in range(200, 300) or response_status == 202:
                err_msg = response_body
            else:
                logger.info(f"Got customer cache for Hawkeye!")

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_cache_for_affecting_monitoring(self):
        last_contact_filter = str(datetime.now() - timedelta(days=7))

        return await self.get_cache(last_contact_filter=last_contact_filter)
