from datetime import datetime
from datetime import timedelta

from shortuuid import uuid

from application.repositories import nats_error_response


class CustomerCacheRepository:
    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_cache(self, *, last_contact_filter: str = None):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {},
        }

        if last_contact_filter:
            request['body']['last_contact_filter'] = last_contact_filter

        try:
            self._logger.info(f"Getting customer cache for Hawkeye...")
            response = await self._event_bus.rpc_request("hawkeye.customer.cache.get", request, timeout=60)
        except Exception as e:
            err_msg = f'An error occurred when requesting customer cache -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300) or response_status == 202:
                err_msg = response_body
            else:
                self._logger.info(f"Got customer cache for Hawkeye!")

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response

    async def get_cache_for_outage_monitoring(self):
        last_contact_filter = str(datetime.now() - timedelta(days=7))

        return await self.get_cache(last_contact_filter=last_contact_filter)
