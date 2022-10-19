import json
import logging
from datetime import datetime, timedelta
from typing import Any

from shortuuid import uuid

from application.repositories import nats_error_response

logger = logging.getLogger(__name__)


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


def get_data_from_response_message(message):
    return json.loads(message.data)


class CustomerCacheRepository:
    def __init__(self, nats_client, config, notifications_repository):
        self._nats_client = nats_client
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_cache(self, *, velo_filter: dict = None):
        err_msg = None

        if not velo_filter:
            velo_filter = {}

        request = {
            "request_id": uuid(),
            "body": {
                "filter": velo_filter,
            },
        }

        try:
            logger.info(f"Getting customer cache for Velocloud host(s) {', '.join(velo_filter.keys())}...")
            response = get_data_from_response_message(
                await self._nats_client.request("customer.cache.get", to_json_bytes(request), timeout=60)
            )
        except Exception as e:
            err_msg = f"An error occurred when requesting customer cache -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status == 202:
                err_msg = response_body
            else:
                logger.info(f"Got customer cache for Velocloud host(s) {', '.join(velo_filter.keys())}!")

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_cache_for_affecting_monitoring(self):
        velocloud_filter = self._config.MONITOR_CONFIG["velo_filter"]
        return await self.get_cache(velo_filter=velocloud_filter)
