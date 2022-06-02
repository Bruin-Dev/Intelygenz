from datetime import datetime, timedelta

from application.repositories import nats_error_response
from shortuuid import uuid


class CustomerCacheRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
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
            if velo_filter:
                self._logger.info(f"Getting customer cache for Velocloud host(s) {', '.join(velo_filter.keys())}...")
            else:
                self._logger.info(f"Getting customer cache for all Velocloud hosts...")
            response = await self._event_bus.rpc_request("customer.cache.get", request, timeout=60)
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
                    self._logger.info(f"Got customer cache for Velocloud host(s) {', '.join(velo_filter.keys())}!")
                else:
                    self._logger.info(f"Got customer cache for all Velocloud hosts!")

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_cache_for_affecting_monitoring(self):
        velocloud_filter = self._config.MONITOR_CONFIG["velo_filter"]
        return await self.get_cache(velo_filter=velocloud_filter)
