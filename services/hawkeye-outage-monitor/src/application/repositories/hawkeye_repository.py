from shortuuid import uuid

from application import nats_error_response


class HawkeyeRepository:

    def __init__(self, event_bus, logger, config, notifications_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository

    async def get_probes(self):
        err_msg = None

        request = {
            "request_id": uuid(),
            "body": {},
        }

        try:
            self._logger.info(f"Getting all probes from Hawkeye...")
            response = await self._event_bus.rpc_request("hawkeye.probe.request", request, timeout=60)
        except Exception as e:
            err_msg = f'An error occurred when requesting all probes from Hawkeye -> {e}'
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = f'Error while retrieving probes: Error {response_status} - {response_body}'
            else:
                self._logger.info("Got all probes from Hawkeye!")

        if err_msg:
            await self.__notify_error(err_msg)

        return response

    async def __notify_error(self, err_msg):
        self._logger.error(err_msg)
        await self._notifications_repository.send_slack_message(err_msg)
