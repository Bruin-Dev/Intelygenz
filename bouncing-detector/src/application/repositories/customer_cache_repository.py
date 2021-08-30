from application.repositories import nats_error_response
from shortuuid import uuid


class CustomerCacheRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_cache(self, velo_filter):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {
                'filter': velo_filter,
            },
        }

        try:
            self._logger.info(f"Getting customer cache for Velocloud host(s) {', '.join(velo_filter.keys())}...")
            response = await self._event_bus.rpc_request("customer.cache.get", request, timeout=60)
        except Exception as e:
            err_msg = f'An error occurred when requesting customer cache -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status == 202:
                err_msg = response_body
            else:
                self._logger.info(f"Got customer cache for Velocloud host(s) {', '.join(velo_filter.keys())}!")

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_cache_for_affecting_monitoring(self):
        velocloud_filter = {self._config.BOUNCING_DETECTOR_CONFIG['velocloud_host']: []}

        return await self.get_cache(velo_filter=velocloud_filter)
