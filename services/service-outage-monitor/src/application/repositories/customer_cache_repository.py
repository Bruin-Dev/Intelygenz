import json
import logging
from datetime import datetime, timedelta

from application.repositories import nats_error_response
from application.repositories.utils_repository import to_json_bytes
from shortuuid import uuid

logger = logging.getLogger(__name__)


class CustomerCacheRepository:
    def __init__(self, nats_client, config, notifications_repository):
        self._nats_client = nats_client
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_cache(self, *, velo_filter: dict = None, last_contact_filter: str = None):
        err_msg = None

        if not velo_filter:
            velo_filter = {}

        request = {
            "request_id": uuid(),
            "body": {
                "filter": velo_filter,
                "last_contact_filter": last_contact_filter,
            },
        }

        try:
            if velo_filter:
                logger.info(f"Getting customer cache for Velocloud host(s) {', '.join(velo_filter.keys())}...")
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
                if velo_filter:
                    logger.info(f"Got customer cache for Velocloud host(s) {', '.join(velo_filter.keys())}!")
                else:
                    logger.info(f"Got customer cache for all Velocloud hosts!")

        if err_msg:
            logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_cache_for_triage_monitoring(self):
        monitoring_filter = self._config.TRIAGE_CONFIG["velo_filter"]

        return await self.get_cache(velo_filter=monitoring_filter)

    async def get_cache_for_outage_monitoring(self):
        monitoring_filter = self._config.MONITOR_CONFIG["velocloud_instances_filter"]
        last_contact_filter = str(datetime.now() - timedelta(days=7))

        return await self.get_cache(velo_filter=monitoring_filter, last_contact_filter=last_contact_filter)
