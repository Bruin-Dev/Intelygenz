from shortuuid import uuid

from application.repositories import nats_error_response


class LitRepository:
    def __init__(self, logger, event_bus, notifications_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._notifications_repository = notifications_repository

    async def get_all_dispatches(self):
        err_msg = None

        request = {
            'request_id': uuid(),
            'body': {},
        }

        try:
            self._logger.info(
                f'Getting all dispatches from LIT...'
            )
            response = await self._event_bus.rpc_request("lit.dispatch.get", request, timeout=30)
            self._logger.info(
                f'Got all dispatches from LIT!'
            )
        except Exception as e:
            err_msg = (
                f'An error occurred when requesting all dispatches from LIT -> {e}'
            )
            response = nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status not in range(200, 300):
                err_msg = (
                    f'Error while retrieving all tickets from LIT in {self._config.ENVIRONMENT.upper()} '
                    f'environment: Error {response_status} - {response_body}'
                )

        if err_msg:
            self._logger.error(err_msg)
            await self._notifications_repository.send_slack_message(err_msg)

        return response
