from shortuuid import uuid

from application.repositories import nats_error_response


class CtsRepository:
    def __init__(self, logger, config, event_bus):
        self._logger = logger
        self._config = config
        self._event_bus = event_bus

    async def get_all_dispatches(self):
        err_msg = None

        # TODO: append also from CTS salesforce
        request = {
            'request_id': uuid(),
            'body': {},
        }

        try:
            self._logger.info(f'Getting all dispatches from CTS...')
            response = await self._event_bus.rpc_request("cts.dispatch.get", request, timeout=30)
            self._logger.info(f'Got all dispatches from CTS!')
        except Exception as e:
            err_msg = (
                f'An error occurred when requesting all dispatches from CTS -> {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while retrieving all tickets from CTS in {self._config.ENVIRONMENT.upper()} '
                    f'environment: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response
