import json
import logging

from shortuuid import uuid

from application.repositories import nats_error_response
from application.repositories.utils_repository import to_json_bytes

logger = logging.getLogger(__name__)


class CustomerCacheRepository:
    def __init__(self, nats_client, config, notifications_repository):
        self._nats_client = nats_client
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_cache(self, filter_: dict = None):
        err_msg = None

        if not filter_:
            filter_ = {}

        request = {
            "request_id": uuid(),
            "body": {
                "filter": filter_,
            },
        }

        try:
            if filter_:
                logger.info(f"Getting customer cache for Velocloud host(s) {', '.join(filter_.keys())}...")
            else:
                logger.info(f"Getting customer cache for all Velocloud hosts...")
            response = await self._nats_client.request("customer.cache.get", to_json_bytes(request), timeout=120)
            response = json.loads(response.data)
        except Exception as e:
            err_msg = f"An error occurred when requesting customer cache -> {e}"
            response = nats_error_response
        else:
            response_body = response["body"]
            response_status = response["status"]

            if response_status == 202:
                err_msg = response_body
            else:
                if filter_:
                    logger.info(f"Got customer cache for Velocloud host(s) {', '.join(filter_.keys())}!")
                else:
                    logger.info(f"Got customer cache for all Velocloud hosts!")

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_cache_for_tnba_monitoring(self):
        monitoring_filter = self._config.MONITOR_CONFIG["velo_filter"]

        return await self.get_cache(filter_=monitoring_filter)
